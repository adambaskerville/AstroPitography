import os
from typing import Literal
import PySimpleGUI as sg
from screeninfo import get_monitors

# set GUI theme
sg.theme('DarkBlack')

# set size of the padding around elements
sg.SetOptions(element_padding=(0, 0),
              text_color = 'Red',
              input_text_color ='Red',
              button_color = ('Black', 'Red'))

# call get_monitors from screensize to extract resolution of Pi
monitor = get_monitors()

# grab the resolution of the screen the program is being run on
SCREEN_WIDTH, SCREEN_HEIGHT =  monitor[0].width, monitor[0].height

# specify folder save location names for images and videos
IMAGE_SAVE_FOLDER: str = "{}/images".format(os.getcwd())
VIDEO_SAVE_FOLDER: str = "{}/videos".format(os.getcwd())

