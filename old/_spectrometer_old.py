import os, sys, math, time
from PIL import Image, ImageDraw, ImageFile, ImageFont
from collections import OrderedDict
from fractions import Fraction
import numpy as np
import colorsys

DEBUG = False
name = sys.argv[1]
im = Image.open(name)
pix = im.load()
draw = ImageDraw.Draw(im)
Width = im.size[0]
Height = im.size[1]

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


def LinearRegression(points_array):
    n = len(points_array)
    x_sum = 0.
    x2_sum = 0.
    y_sum = 0.
    y2_sum = 0.
    xy_sum = 0.

    for i in range(0, n):
        x = points_array[i].x
        y = points_array[i].y
        x_sum += x
        x2_sum += x * x

        y_sum += y
        y2_sum += y * y

        xy_sum += y * x

    num_n = y_sum * x2_sum - x_sum * xy_sum
    den_n = n * x2_sum - x_sum * x_sum

    num_m = n * xy_sum - x_sum * y_sum
    den_m = n * x2_sum - x_sum * x_sum
    return num_m / den_m, num_n / den_n


def SpectrumBoundY(pix, width, height, threshold):
    top_scatter = []
    bottom_scatter = []
    for x in range(0, width):
        point_top = Point(-1, -1)
        point_bot = Point(-1, -1)

        # Top of the spectrum
        for y in range(0, height / 2):
            r, g, b = pix[x, y]
            intensity = r + g + b
            if intensity > threshold:
                point_top.x = x
                point_top.y = y
                break

        for y in range(height - 1, height / 2, -1):
            r, g, b = pix[x, y]
            intensity = r + g + b
            if intensity > threshold:
                point_bot.x = x
                point_bot.y = y
                break

        if point_bot.is_between(width, 0, height, 0):
            bottom_scatter.append(point_bot)
        if point_top.is_between(width, 0, height, 0):
            top_scatter.append(point_top)

    # first line
    m_top, n_top = LinearRegression(top_scatter)
    m_bot, n_bot = LinearRegression(bottom_scatter)
    global DEBUG
    if DEBUG:
        for p in top_scatter:
            draw.point((p.x, p.y), 'white')
        for p in bottom_scatter:
            draw.point((p.x, p.y), 'white')
    global m_up, n_up, m_down, n_down
    m_up = m_bot
    n_up = n_bot

    m_down = m_top
    n_down = n_top
    return (m_top, n_top), (m_bot , n_bot)


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


    thresholds = [ 405, 435, 487, 545, 585, 610, 780 ];
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

m_up = 0
n_up = 0

m_down = 0
n_down = 0

def Up(x_val):
    return x_val * m_up + n_up
def Down(x_val):
    return x_val * m_down + n_down

# Get Bounds
top_line, bot_line = SpectrumBoundY(pix, im.size[0], im.size[1], 100)

# Line count is the lines needed to sample the image + 1
#                                       (ex: if nedded 15 lines then the line_count is 16)
line_count = 16
slopes = []
intercepts = []

# TODO: Add Weights
weights = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05]
w_sum = 0.0
for i in range(len(weights)):
    w_sum += weights[i]

theta_diff = math.atan(m_up) - math.atan(m_down)
theta_diff /= -float(line_count)

for i in range(1, line_count):
    slopes.append(math.tan(math.atan(m_up) + theta_diff * i))
    intercepts.append(i * abs(n_up - n_down) / (float(line_count)) + n_down)

def mid(val, slope, n):
    return val * slope + n

def i_mid(y_val, slope, n):
    return (val - n) / slope


chart = Image.new('RGB', (Width, Height), (255,255,255))
_draw = ImageDraw.Draw(chart)


# THIS IS FOR SETTING PIXEL MAX AND PIXEL MIN, DELETE THIS AND ADD GIVE PIXELMAX PIXELMIN
# arr = []
# pix_min = 480
# pix_max = 900
pix_min = Width / 3 - 75
pix_max = 17
# Threshold
TH = 70
g_peak = 0
g_peak_pixel = 0

for x in range(0, Width):
    y = mid(x, slopes[7], intercepts[7])
    r, g, b = pix[x, y]
    intensity = r + g + b
    if g > g_peak:
        g = g_peak
        g_peak_pixel = x
# print g_peak_pixel

for x in range(0, Width):
    y = mid(x, slopes[7], intercepts[7])
    r, g, b = pix[x, y]
    intensity = r + g + b
    if (intensity > TH):
        pix_min = x
        break

for x in range(Width - 1, 0, -1):
    y = mid(x, slopes[7], intercepts[7])
    r, g, b = pix[x, y]
    intensity = r + g + b
    if (r > TH):
        pix_max = x
        break
# THIS IS FOR SETTING PIXEL MAX AND PIXEL MIN, DELETE THIS AND ADD GIVE PIXELMAX PIXELMIN
pix_min = 690
pix_max = 1150

# print pix_min
# print pix_max
file = open("output.csv", 'w')
file.write("Wavelength\tIntensity\n")
# this is for horizontal shifting to plot wavelength graph on top of output image. See Line #HS1
SHIFT = 600
for x in range(pix_min, pix_max):
    y = 0.0
    y = float(mid(x, slopes[7], intercepts[7]))
    r, g, b = pix[x, y]
    intensity = r + g + b
    nm = PixelToWaveLength(x, (pix_min, pix_max), (405, 620))
    draw.point((x, (Height - intensity/2) ),fill='white')
    _draw.line((x, Height, x, (Height - intensity / 2)), fill=wavelengthToColor(nm))
    # HS1
    draw.line((x, Height - SHIFT, x, (Height - intensity / 2) - SHIFT), fill=wavelengthToColor(nm))
    file.write(str(x - pix_min) + "\t" + str(nm) + "\t" + str(float(intensity) / (255.0 * 3.0)) + "\n")

for i in range(len(slopes)):
    draw.line((0, mid(0, slopes[i], intercepts[i]), Width, mid(Width, slopes[i], intercepts[i])),fill="#888")
draw.line((0, Up(0), Width, Up(Width)),fill="#888")
draw.line((0, Down(0), Width, Down(Width)),fill="#888")


draw.line((pix_min, 0, pix_min, Height),fill='white')
draw.line((pix_max, 0, pix_max, Height),fill='white')

chart.save("chart.jpeg", "JPEG", quality=80, optimize=True, progressive=True)
im.save("output.jpg", "JPEG", quality=80, optimize=True, progressive=True)
