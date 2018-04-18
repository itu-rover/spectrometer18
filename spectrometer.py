import os, sys, math, time
from PIL import Image, ImageDraw, ImageFile, ImageFont
from collections import OrderedDict
from fractions import Fraction
import numpy as np
import colorsys

DEBUG = True
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


def SpectrumBoundX(pix, width, height, b_threshold, r_threshold):
    top_scatter = []
    bottom_scatter = []
    for y in range(0, height):
        point_top = Point(-1, -1)
        point_bot = Point(-1, -1)

        # Top of the spectrum
        for x in range(0, width / 2):
            r, g, b = pix[x, y]
            intensity = b
            # print Down(x), y
            in_between = y <= Up(x) and y >= Down(x)
            if intensity > b_threshold and in_between:
                point_top.x = x
                point_top.y = y
                break

        for x in range(width - 1, width / 2, -1):
            r, g, b = pix[x, y]
            intensity = r
            in_between = y <= Up(x) and y >= Down(x)
            if intensity > r_threshold and in_between:
                point_bot.x = x
                point_bot.y = y
                break

        if point_bot.is_between(width, 0, height, 0):
            bottom_scatter.append(point_bot)
        if point_top.is_between(width, 0, height, 0):
            top_scatter.append(point_top)

    # first line
    m_top, n_top = LinearRegression(top_scatter, True)
    m_bot, n_bot = LinearRegression(bottom_scatter, True)
    global DEBUG
    if DEBUG:
        for p in top_scatter:
            draw.point((p.x, p.y), 'white')
        for p in bottom_scatter:
            draw.point((p.x, p.y), 'white')
    global m_left, n_left, m_right, n_right
    m_left = m_top
    m_right = m_bot
    n_left = n_top
    n_right = n_bot
    return (m_top, n_top), (m_bot , n_bot)


def LinearRegression(points_array, invert):
    n = len(points_array)
    x_sum = 0.
    x2_sum = 0.
    y_sum = 0.
    y2_sum = 0.
    xy_sum = 0.

    for i in range(0, n):
        x = 0.
        y = 0.
        if invert:
            x = points_array[i].y
            y = points_array[i].x
        else:
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
    m_top, n_top = LinearRegression(top_scatter, False)
    m_bot, n_bot = LinearRegression(bottom_scatter, False)
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

def DrawLinesX((m_top, n_top), (m_bot, n_bot)):
    # m_top = - 1.0 / m_top
    # m_bot = - 1.0 / m_bot

    def top_eqX(value):
        return m_top * value + n_top
    def bot_eqX(value):
        return m_bot * value + n_bot

    def i_topX(value):
        return (value - n_top) / float(m_top)
    def i_botX(value):
        return (value - n_bot) / float(m_bot)

    global draw
    # draw.line((i_topX(0), 0, i_topX(500), 500),fill="#888")
    # draw.line((bot_eqX(0), 0, bot_eqX(Height), Height),fill="#888")
    # draw.line((top_eqX(0), 0, top_eqX(Height), Height),fill="#888")

    # draw.line((0, i_topX(0), Height, i_topX(Height)),fill="#888")
    # draw.line((bot_eqX(0), 0, bot_eqX(Height), Height),fill="#888")


def PixeloWaveLength(pixel_x, (pixel_min, pixel_max), (wave_min, wave_max)):
    # h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    # print h,s,v
    # wave_dif = float(wave_max) - float(wave_min)
    # return wave_max - wave_dif / 270.0 * float(h)
    scalar = float(pixel_x - pixel_min) / float(pixel_max - pixel_min)
    return scalar * float(wave_max - wave_min) + wave_min

m_left = 0
n_left = 0

m_right = 0
n_right = 0

m_up = 0
n_up = 0

m_down = 0
n_down = 0

def Left(y_val):
    return y_val * m_left + n_left
def Right(y_val):
    return y_val * m_right + n_right

def Up(x_val):
    return x_val * m_up + n_up
def Down(x_val):
    return x_val * m_down + n_down

# Get Bounds
top_line, bot_line = SpectrumBoundY(pix, im.size[0], im.size[1], 100)
# top_line_x, bot_line_x = SpectrumBoundX(pix, im.size[0], im.size[1], 100, 100)
# DrawLinesX(top_line_x, bot_line_x)
# DrawLinesY(top_line, bot_line)
print PixeloWaveLength(100, (100, 200), (380, 750))
draw.line((0, Up(0), Width, Up(Width)),fill="#888")
draw.line((0, Down(0), Width, Down(Width)),fill="#888")
# draw.line((Left(0), 0, Left(Height), Height),fill="#888")
# draw.line((Right(0), 0, Right(Height), Height),fill="#888")


slopes = []
intercepts = []
slopes.append((m_up + m_down) / 2.0)
intercepts.append((n_up + n_down) / 2.0)

for i in range(1, 3):
    slopes.append((slopes[i - 1] + m_up) / 2)
    intercepts.append((intercepts[i - 1] + n_up) / 2)

def mid(val, slope, n):
    return val * slope + n

for i in range(len(slopes)):
    draw.line((0, mid(0, slopes[i], intercepts[i]), Width, mid(Width, slopes[i], intercepts[i])),fill="#888")




im.save("output.jpg", "JPEG", quality=80, optimize=True, progressive=True)
