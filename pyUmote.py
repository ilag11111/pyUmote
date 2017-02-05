#!/usr/bin/env python

import xwiimote
import uinput
import umote
import select
import os, os.path
import ConfigParser

screen_opt_default = {
    'emitter_width_mm' : 195,
    'emitter_position' : 'top',
    'emitter_offset_mm' : 25,
    'screen_width_mm' : 510,
    'screen_height_mm' : 287,
}

mote_opt_default = {
    'ir_vcomp' : True ,
    'ir_mouse_emu' : False
}
    
dirs = [
    os.environ['HOME']+"/.config/pyUmote",
    "/etc/pyUmote"
]

def freeslot():
    for i in [0,1,2,3]:
        if umotes[i] is None:
            return i
    return -1

def monitorLoop():
    mote_path = mon.poll()
    while mote_path is not None:
        index=freeslot()
        newUmote=umote.umote(index,mote_path,mote_opt[index],screen_opt)
        p.register(newUmote.get_fd(), select.POLLIN)
        umotes[index]=newUmote
        mote_path = mon.poll()
    return

def loadCfg(name,default):
    cfg={}
    path=getPath(name)
    if path is None:
        cfg=default
    else:
        parser=ConfigParser.SafeConfigParser()
        parser.read(path)
        for key in default.keys():
            try:
                if type(default[key]) is str:
                    cfg[key]=parser.get(name,key)
                elif type(default[key]) is int:
                    cfg[key]=parser.getint(name,key)
                elif type(default[key]) is bool:
                    cfg[key]=parser.getboolean(name,key)
            except ConfigParser.NoOptionError:
                cfg[key]=default[key]
    return cfg

def loadMoteCfg(index):
    return mote_opt_default

def getPath(name):
    for path in dirs:
        if os.path.isfile(path+"/"+name+".cfg"):
            return path+"/"+name+".cfg"
    return None

p = select.poll()
umotes = [None,None,None,None]
mon = xwiimote.monitor(True, False)
mon_fd = mon.get_fd(False)
p.register(mon_fd, select.POLLIN)

print ("Monitor initiated")

screen_opt = loadCfg("screen",screen_opt_default)
mote_opt_default = loadCfg("mote_default",mote_opt_default)

mote_opt=[None,None,None,None]
for i in [0,1,2,3]:
    mote_opt[i]=loadCfg("mote"+str(i+1),mote_opt_default)
        
monitorLoop()

try:
    while True:
        # Poll global monitor, add as appropriate
        polls = p.poll()
        for fd,evt in polls:
            if fd == mon_fd :
                monitorLoop()
            else:
                for mote in umotes:
                    if mote is None:
                        continue
                    if fd == mote.get_fd():
                        if mote.dispatch():
                            p.unregister(mote.get_fd())
                            umotes[mote.index]=None
                            del mote
                                
except KeyboardInterrupt:
    print "exiting..."

# cleaning
for mote in umotes:
    if mote is None:
        continue
    p.unregister(mote.get_fd())
    umotes[mote.index]=None
    del mote
exit(0)
