# Installation
Move this folder into home folder.
'''$ mv ../rpi_capture_cam ~/spectrometer'''

The folder tree should look like
/home/pi/spectrometer
    cam.py
    light.py
    samples/

Enter the directory
'''$ cd $HOME/spectrometer'''

move the capture command to /bin
'''$ sudo mv capture /bin'''

The folder tree should look like

/bin
    capture

to make sure it is copied in the right directory
'''$ sudo ls /bin | grep capture''' should result:
"capture"


then source the terminal.
'''$ source ~/.bashrc'''



# Usage
To run:
'''$ capture FILE_NAME'''


# Simple Documentation
    The capture script simply runs few lines of code to first
activate the light wait few sec and run camera capturing and turn light off.
The file will be generated in /samples
