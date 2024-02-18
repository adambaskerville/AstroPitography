import os
from typing import Literal
import PySimpleGUI as sg

# set GUI theme
sg.theme('DarkBlack')

# set size of the padding around elements
sg.SetOptions(element_padding=(0, 0),
              text_color = 'Red',
              input_text_color ='Red',
              button_color = ('Black', 'Red'))

# grab the resolution of the screen the program is being run on
SCREEN_WIDTH, SCREEN_HEIGHT = sg.Window.get_screen_size()

# specify folder save location names for images and videos
IMAGE_SAVE_FOLDER: str = "{}/images".format(os.getcwd())
VIDEO_SAVE_FOLDER: str = "{}/videos".format(os.getcwd())

RESOLUTION_OPTIONS = ["640 x 480", "1280 x 720", "1920 x 1080", "2560 x 1440"]
