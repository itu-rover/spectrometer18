from picamera import PiCamera
import sys
import os
from time import sleep

# camera.AWB_MODES # White balances
# off, auto, sunlight, cloudy, shade, tungsten, fluorescent, incandescent, flash, and horizon

# camera.EXPOSURE_MODES # Exposure modes
# off, auto, night, nightpreview, backlight, spotlight, sports, snow,
# beach, verylong, fixedfps, antishake, and fireworks. The default is auto

name = sys.argv[1] # JPG format
camera = PiCamera()

path = name + ".jpg"
# if not os.path.exists("samples/" + name):
#     os.makedirs("samples/" + name)

camera.start_preview()
camera.awb_mode = 'flash'
camera.exposure_mode = 'off'
camera.shutter_speed = int(sys.argv[2])
camera.contrast = 0
camera.brightness = 50
sleep(1)
camera.capture(path)
camera.stop_preview()
print camera.shutter_speed
print camera.exposure_mode
