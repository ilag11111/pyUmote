# pyUmote
A python-based userland driver for the Wiimote with perfect iR tracking.

## What does this do?
It turns your Wiimote into a fully-usable Linux gamepad which is fully configurable in userland, without needing to restart X or the entire OS.

### What does it support?
All Wiimote buttons and sensors
Perfect to the millimeter IR tracking
Nunchuck and all sensors
Basic Motion Plus support
Mouse Emulation for IR tracking
Hotplugging support

### What does it not support?
Classic controllers and any other peripherals I don't have access to.

## How do I use it
./pyUmote.py
If you get a permission error, run with sudo as a quick fix or mess with your udev rules until it goes away.  You're on your own with that.

###Dependencies
Install these with a package manager or pip if you can:
* [xwiimote](https://github.com/dvdhrm/xwiimote)
* [xwiimote-bindings](https://github.com/dvdhrm/xwiimote-bindings)
* [python-uinput](https://github.com/tuomasjjrasanen/python-uinput)

## Configuration
Configuration files are searched for in ~/.config/pyUmote and /etc/pyUmote.  If none are found, sane defaults will be used, but iR tracking will be nowhere near close
### screen.cfg
* [screen]
* emitter_width_mm - The width of the iR emitter, measured from the center of both emitting sides.  On the official sensor bar, this is about 195mm.
* emitter_position - top or bottom - where the iR emitter is places relative to your screen.  This is ignored if ir_vcomp is False in mote#.cfg
* emitter_offset_mm - How far above or below the screen the iR emitter is. This is ignored if ir_vcomp is False in mote#.cfg
* screen_width_mm - The width of your screen in mm.  This is sometimes reported by xrandr.
* screen_height_mm - The height of your screen in mm.  This is sometimes reported by xrandr.

### mote_default.cfg, mote#.cfg [#=1-4]
* [mote#]
* ir_vcomp - True or False.  Enable vertical compensation, which is what makes the tracking perfect to the screen.  If disabled, the iR vertical center will be when the wiimote is pointed directly at the sensor bar.
* ir_mouse_emu - True or False.  Use the iR sensor data to directly move the mouse pointer.  If false, the iR data will instead appear as additional axes.

## Troubleshooting
### iR tracking is nowhere near perfect, what gives?
Read configuration above.
### I have multiple monitors, but the iR mouse files across all monitors instead of just the one
You'll have to mess with coordinate transformation matricies.  It's not fun stuff.  Here's a sample which fixes it for my side-by-side dual monitor setup.  The rest is up to you.
* xinput set-prop "Umote 1 iR Mouse" --type=float "Coordinate Transformation Matrix" 0.5 0 0 0 1 0 0 0 1

### I want to emulate keystrokes or mouse buttons.  How do I?
At this time, pyUmote only supports emulating mouse movement through the iR sensor as a non-default option.  For everything else, use a program like [antimicro](https://github.com/AntiMicro/antimicro).
