import os
import sys
import correlation
import examination
# state = "CAPTURE"
filename = sys.argv[1]
state = sys.argv[2]
EXPOSURE = 100000

def send_command(command, host="itu-rover@itu-rover-asus.local"):
    signal_command = "ssh pi@raspberrypi.local " + "'" + command + "'"
    print """echo " """ + signal_command + """ " | ssh """ + host
    # print("ssh " + host + " '" + signal_command + "'")
def scp(host_directory, target_directory):
    pass

# print "ssh itu-rover@itu-rover-asus.local " + "'" + capture_cam_command + "'"
# os.system("ssh itu-rover@itu-rover-asus.local " + "'" + capture_cam_command + "'")

if state == "EXAMINE":
    command_to_capture = "python /home/pi/spectrometer/capture_camera.py " + str(filename) + " " + str(EXPOSURE)
    send_command(command_to_capture)
    scp("/home/pi/spectrometer/*.jpg", "samples/")
    examination.examine(filename)
    result = correlation.calculate(filename)
    for line in result:
        print line

elif state == "MULTIEX":
     for path in os.listdir("samples/" + filename):
         if path != ".DS_Store":
             examination.examine(path.split(".")[0], filename)
elif state == "LOAD":
    send_command(command_to_capture)
    scp("/home/pi/spectrometer/*.jpg", "samples/")
    examination.examine(filename)
    os.system("cp -r results/" + filename + " dataset/")
elif state == "COMPARE":
    result = correlation.calculate(filename)
    for line in result:
        print line
