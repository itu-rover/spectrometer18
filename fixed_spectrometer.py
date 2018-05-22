import os, sys, math, time
from PIL import Image, ImageDraw, ImageFile, ImageFont
from collections import OrderedDict
from fractions import Fraction
import numpy as np
import colorsys

#import pandas


DEBUG = False
project_name = "results/" + sys.argv[1] + "/"
name = "samples/" + sys.argv[1] + ".jpg"
im = Image.open(name)
pix = im.load()
draw = ImageDraw.Draw(im)
Width = im.size[0]
Height = im.size[1]


if not os.path.exists("results/" + sys.argv[1]):
    os.makedirs("results/" + sys.argv[1])

class Point(object):
    """
    Simple point library
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_between(self, x_top, x_bot, y_top, y_bot):
        b1 = self.x >= x_bot and self.x <= x_top
        b2 = self.y >= y_bot and self.y <= y_top
        if b1 and b2:
            return True
        else:
            return False


def DrawLinesY((m_top, n_top), (m_bot, n_bot)):
    def top_eqY(value):
        return m_top * value + n_top
    def bot_eqY(value):
        return m_bot * value + n_bot

    global draw
    draw.line((0, top_eqY(0), Width, top_eqY(Width)),fill="#888")
    draw.line((0, bot_eqY(0), Width, bot_eqY(Width)),fill="#888")


def wavelengthToColor(lambda2):
    # Based on: http://www.efg2.com/Lab/ScienceAndEngineering/Spectra.htm
    # The foregoing is based on: http://www.midnightkite.com/color.html
    factor = 0.0;

    color=[0,0,0]
    # Original
    # thresholds = [ 380, 440, 490, 510, 580, 645, 780 ];

    global thresholds
    #thresholds = [ 380, 440, 490, 510, 580, 610, 780 ];
    #                    vio  blu  cyn  gre  yel  end
    # thresholds = [380, 400, 450, 465, 520, 565, 780];
    for i in range(0, len(thresholds)-1, 1):
        t1 = thresholds[i]
        t2 = thresholds[i+1]
        if (lambda2 < t1 or lambda2 >= t2):
        	continue
        if (i % 2 != 0):
        	tmp = t1
        	t1 = t2
        	t2 = tmp
        if i<5:
        	color[i % 3] = (lambda2 - t2) / (t1 - t2)
        color[2 - i / 2] = 1.0;
        factor = 1.0;
        break


    # Let the intensity fall off near the vision limits
    if (lambda2 >= 380 and lambda2 < 420):
        factor = 0.2 + 0.8 * (lambda2 - 380) / (420 - 380);
    elif (lambda2 >= 600 and lambda2 < 780):
        factor = 0.2 + 0.8 * (780 - lambda2) / (780 - 600);
    return (int(255 * color[0] * factor), int(255 * color[1] * factor), int(255 * color[2] * factor))


def PixelToWaveLength(pixel_x, (pixel_min, pixel_max), (wave_min, wave_max)):
    # h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    # print h,s,v
    # wave_dif = float(wave_max) - float(wave_min)
    # return wave_max - wave_dif / 270.0 * float(h)
    scalar = float(pixel_x - pixel_min) / float(pixel_max - pixel_min)
    return scalar * float(wave_max - wave_min) + wave_min


# System Setup
spectrum_angle = 0
spectrum_aperture = 340
# spectrum_aperture = 385
spectrum_min = 405
pix_min = 600
pix_max = pix_min + 460
PLOT_SHIFT = 850
thresholds = [ 405, 435, 487, 545, 585, 610, 780 ];
intensity_threshold = 55

# Code begin
m_up = 0
n_up = 0

m_down = 0
n_down = 0
spectrum_radians = math.radians(spectrum_angle)
m_up = math.tan(spectrum_radians)
m_down = math.tan(spectrum_radians)
n_up = spectrum_min
n_down = spectrum_min + spectrum_aperture

def Up(x_val):
    return x_val * m_down + n_down
def Down(x_val):
    return x_val * m_up + n_up

# Line count is the lines needed to sample the image + 1
#                                       (ex: if nedded 15 lines then the line_count is 16)
line_count = 16
slopes = []
intercepts = []

theta_diff = math.atan(m_up) - math.atan(m_down)
theta_diff /= -float(line_count)

for i in range(1, line_count + 1):
    slopes.append(math.tan(math.atan(m_up) + theta_diff * i))
    intercepts.append(i * abs(n_up - n_down) / (float(line_count)) + n_up)

def mid(val, slope, n):
    return val * slope + n

def i_mid(y_val, slope, n):
    return (val - n) / slope


chart = Image.new('RGB', (Width, Height), (255,255,255))
_draw = ImageDraw.Draw(chart)

file = open(project_name + "output.csv", 'w')
# Write to file the head
file.write("count\twavelength\tintensity\n")

# The percentage is based on white_raw data
white_raw = open("white_raw/white_raw.csv", 'r')
# Ignore First Line
white_raw.readline()

for x in range(pix_min, pix_max):
    intensity = 0.0
    y = 0.0
    threshold_exceeded_linecount = 0
    for n in range(line_count):
        y = float(mid(x, slopes[n], intercepts[n]))
        r, g, b = pix[x, y]
        if (r + g + b) > intensity_threshold:
            intensity += r + g + b
            threshold_exceeded_linecount += 1
            draw.point((x, y),fill='white')
    if threshold_exceeded_linecount == 0:
        intensity = 0
    else:
        intensity /= float(threshold_exceeded_linecount)
    # WARNING: This has fixed value of 405-780, it should be dynamically ranged
    nm = PixelToWaveLength(x, (pix_min, pix_max), (405, 780))

    # Base value, white paper
    white_y = float(white_raw.readline().split("\t")[2])
    # white_y = 100

    # Plot scatter, white: white paper, green: actual data
    draw.point((x, (Height - intensity / 2) ),fill='red')
    draw.point((x, (Height - white_y / 2)),fill='white')

    # Draw to the chart
    _draw.line((x, Height, x, (Height - 100 * (intensity / white_y) * 2)), fill=wavelengthToColor(nm))

    # Draw the graph on original image
    draw.line(( x, Height - PLOT_SHIFT, x, (Height - 100 * (intensity / white_y) * 2) - PLOT_SHIFT), fill=wavelengthToColor(nm))

    # file.write(str(x - pix_min) + "\t" + str(nm) + "\t" + str(float(intensity) / (255.0 * 3.0)) + "\n")
    # Write the percentage based on white_raw
    file.write(str(x - pix_min) + "\t" + str(nm) + "\t" + str(float(100 * (intensity / white_y))) + "\n")

# Print calculator lines
for i in range(len(slopes)):
    # FIXME: uncomment it
    # WARNING: COMMENT THIS TO HIDE LINES
    draw.line((0, mid(0, slopes[i], intercepts[i]), Width, mid(Width, slopes[i], intercepts[i])),fill="#888")

# Print horizontal lines
draw.line((0, Up(0), Width, Up(Width)),fill="#888")
draw.line((0, Down(0), Width, Down(Width)),fill="#888")

# Print Vertical Lines
draw.line((pix_min, 0, pix_min, Height),fill='white')
draw.line((pix_max, 0, pix_max, Height),fill='white')

# Save outputs
chart.save(project_name + "chart.jpeg", "JPEG", quality=80, optimize=True, progressive=True)
im.save(project_name + "output.jpg", "JPEG", quality=80, optimize=True, progressive=True)
