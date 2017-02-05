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
Please inspect the files in sample-cfg.

## Troubleshooting
### iR tracking is nowhere near perfect, what gives?
Read configuration above.

### Even after configuration, iR tracking only works in a limited section of the screen
Move backwards.

### I have multiple monitors, but the iR mouse files across all monitors instead of just the one
You'll have to mess with coordinate transformation matricies.  It's not fun stuff.  Here's a sample which fixes it for my side-by-side dual monitor setup.  The rest is up to you.
* xinput set-prop "Umote 1 iR Mouse" --type=float "Coordinate Transformation Matrix" 0.5 0 0 0 1 0 0 0 1

### I want to emulate keystrokes or mouse buttons.  How do I?
At this time, pyUmote only supports emulating mouse movement through the iR sensor as a non-default option.  For everything else, use a program like [antimicro](https://github.com/AntiMicro/antimicro).
