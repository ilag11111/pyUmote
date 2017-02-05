import uinput
import xwiimote
import errno
import math

class umote:
	def __init__(self,index,path,mote_opt,screen_opt):
		self.index=index
		self._path=path
		self._screen_opt=screen_opt
		self._mote_opt=mote_opt
		self._dev=xwiimote.iface(self._path)
		self._uinput_create()
		print "uMote connected"
	def __enter__(self):
		return self
	def _setLED(self,num):
		for i in [1,2,3,4]:
			self._dev.set_led(i,False)
		self._dev.set_led(num,True)
	def get_fd(self):
		return self._dev.get_fd()
	def _uinput_create(self):
		if hasattr(self,'_uinput'):
			self._uinput.destroy()
		if hasattr(self,'_uinput_mouse'):
			self._uinput_mouse.destroy()
		buttons=[
			uinput.ABS_HAT0X + (-1,1,0,0),
			uinput.ABS_HAT0Y + (-1,1,0,0),
			uinput.BTN_A,
			uinput.BTN_B,
			uinput.BTN_MODE,
			uinput.BTN_START,
			uinput.BTN_SELECT,
			uinput.BTN_1,
			uinput.BTN_2,
			uinput.BTN_C,
			uinput.BTN_Z,
			uinput.ABS_X + (-100,100,0,0),
			uinput.ABS_Y + (-100,100,0,0),
			uinput.ABS_RX + (-512,512,0,0),
			uinput.ABS_RY + (-512,512,0,0),
			uinput.ABS_RZ + (-512,512,0,0),
			uinput.ABS_THROTTLE + (-512,512,0,0),
			uinput.ABS_RUDDER + (-512,512,0,0),
			uinput.ABS_WHEEL + (-512,512,0,0),
			uinput.ABS_HAT1X,
			uinput.ABS_HAT1Y,
			uinput.ABS_HAT2X,
			]
		if self._mote_opt['ir_mouse_emu']:
			self._uinput_mouse=uinput.Device([
				uinput.BTN_LEFT,
				uinput.BTN_RIGHT,
				uinput.BTN_MIDDLE,
				uinput.ABS_X+(0,65535,0,0),
				uinput.ABS_Y+(0,65535,0,0),
				], "Umote "+str(self.index)+" iR Mouse")
		else:
			buttons.append(uinput.ABS_TILT_X+(0,65535,0,0))
			buttons.append(uinput.ABS_TILT_Y+(0,65535,0,0))
		self._uinput=uinput.Device(buttons,"Umote "+str(self.index))
	def dispatch(self):
		event=xwiimote.event()
		try:
			self._dev.dispatch(event)
			if event:
				return self._processEvent(event)
		except IOError as e:
			if e.errno != errno.EAGAIN:
				print e
				return 1
			if self._dev.opened() != self._dev.available():
				self._dev.open(self._dev.available())
				self._setLED(self.index+1)
				#TODO: CC Devices
			
	def _processEvent(self,event):
		if event.type == xwiimote.EVENT_KEY or event.type == xwiimote.EVENT_NUNCHUK_KEY:
			(code, state) = event.get_key()
			if code == xwiimote.KEY_LEFT:
				code=uinput.ABS_HAT0X
				state*=-1
			elif code == xwiimote.KEY_RIGHT:
				code=uinput.ABS_HAT0X
			elif code == xwiimote.KEY_UP:
				code=uinput.ABS_HAT0Y
				state*=-1
			elif code == xwiimote.KEY_DOWN:
				code=uinput.ABS_HAT0Y
			elif code == xwiimote.KEY_A:
				code=uinput.BTN_A
			elif code == xwiimote.KEY_B:
				code=uinput.BTN_B
			elif code == xwiimote.KEY_PLUS:
				code=uinput.BTN_START
			elif code == xwiimote.KEY_MINUS:
				code=uinput.BTN_SELECT
			elif code == xwiimote.KEY_HOME:
				code=uinput.BTN_MODE
			elif code == xwiimote.KEY_ONE:
				code=uinput.BTN_1
			elif code == xwiimote.KEY_TWO:
				code=uinput.BTN_2
			elif code == xwiimote.KEY_C:
				code=uinput.BTN_C
			elif code == xwiimote.KEY_Z:
				code=uinput.BTN_Z
			self._uinput.emit(code,state)
			return
		elif event.type == xwiimote.EVENT_IR:
			left=[]
			right=[]
			for i in [0,1,2,3]:
				(x,y,z) = event.get_abs(i)
				
				#if not self._dev.ir_is_valid(i):
				if x==y==1023 or x==y==0:
					continue
					
				if left==[] or left[0]>x or (left[0]==x and left[1]>y):
					left=[x,y]
					
				if right==[] or right[0]<x or (right[0]==x and right[1]>y):
					right=[x,y]

			avg=[0,0]
			if not left==right==[] and not left==right:
				#Get Pixels per mm
				distx=right[0]-left[0]
				disty=left[1]-right[1]
				dist=math.sqrt(distx*distx + disty*disty)
				ppmm=dist/self._screen_opt['emitter_width_mm']
				
				# Rotation correction
				angle=math.atan2((right[1]-left[1]),(right[0]-left[0]))
				
				##Translate points to make center (0,0)
				left[0]-=512
				right[0]-=512
				left[1]-=384
				right[1]-=384
				
				##Convert points to Polar Coordinatse
				polL=[math.sqrt(left[0]**2+left[1]**2),math.atan2(left[1],left[0])]
				polR=[math.sqrt(right[0]**2+right[1]**2),math.atan2(right[1],right[0])]
				
				##Rotate
				polL[1]-=angle
				polR[1]-=angle
				
				##Back to cart
				left=[int(polL[0]*math.cos(polL[1])),int(polL[0]*math.sin(polL[1]))]
				right=[int(polR[0]*math.cos(polR[1])),int(polR[0]*math.sin(polR[1]))]
				
				##Translate back to proper position
				left[0]+=512
				right[0]+=512
				left[1]+=384
				right[1]+=384

				#Set Calibration
				screenLeft=512-ppmm*self._screen_opt['screen_width_mm']/2
				screenRight=512+ppmm*self._screen_opt['screen_width_mm']/2
				if self._mote_opt['ir_vcomp']:
					if self._screen_opt['emitter_position'] == 'top':
						screenTop=384+ppmm*self._screen_opt['emitter_offset_mm']
						screenBottom=screenTop+ppmm*self._screen_opt['screen_height_mm']
					else:
						screenBottom=384-ppmm*self._screen_opt['emitter_offset_mm']
						screenTop=screenBottom-ppmm*self._screen_opt['screen_height_mm']
				else:
					screenTop=384-ppmm*self._screen_opt['screen_height_mm']
					screenBottom=384+ppmm*self._screen_opt['screen_height_mm']
				
				#Get average
				avg[0]=(left[0]+right[0])/2
				avg[1]=(left[1]+right[1])/2
				
				#Get ratio
				avg[0]=self._rat_finder(screenLeft,screenRight,avg[0])
				avg[1]=self._rat_finder(screenTop,screenBottom,avg[1])
				
				#Translate to +/- 32767
				avg[0]*=65535
				avg[1]*=65535
				
				#emit
				if self._mote_opt['ir_mouse_emu']:
					self._uinput_mouse.emit(uinput.ABS_X,int(65535-avg[0]))
					self._uinput_mouse.emit(uinput.ABS_Y,int(avg[1]))
				else:
					self._uinput.emit(uinput.ABS_TILT_X,int(65535-avg[0]))
					self._uinput.emit(uinput.ABS_TILT_Y,int(avg[1]))
			return
		elif event.type == xwiimote.EVENT_ACCEL:
			(x,y,z) = event.get_abs(0)
			self._uinput.emit(uinput.ABS_RX,x)
			self._uinput.emit(uinput.ABS_RY,y)
			self._uinput.emit(uinput.ABS_RZ,z)
		elif event.type == xwiimote.EVENT_NUNCHUK_MOVE:
			(x,y,z) = event.get_abs(0)
			self._uinput.emit(uinput.ABS_X,x)
			self._uinput.emit(uinput.ABS_Y,y)
			(x,y,z) = event.get_abs(1)
			self._uinput.emit(uinput.ABS_THROTTLE,x)
			self._uinput.emit(uinput.ABS_RUDDER,y)
			self._uinput.emit(uinput.ABS_WHEEL,z)
		elif event.type == xwiimote.EVENT_MOTION_PLUS:
			(x,y,z) = event.get_abs(0)
			self._uinput.emit(uinput.ABS_HAT1X,x)
			self._uinput.emit(uinput.ABS_HAT1Y,y)
			self._uinput.emit(uinput.ABS_HAT2X,z)
		elif event.type == xwiimote.EVENT_GONE:
			return 1
		return
	def _rat_finder(self,min,max,val):
		val-=min
		max-=min
		return val/max
	def __exit__(self, exc_type, exc_value, traceback):
		self._dev.close(self._dev.available())
		self._uinput.destroy()
		print "umote disconnected"	
	def __del__(self):
		self._dev.close(self._dev.available())
		self._uinput.destroy()
		if hasattr(self,'_uinput_mouse'):
			self._uinput_mouse.destroy()
		print "umote disconnected"
