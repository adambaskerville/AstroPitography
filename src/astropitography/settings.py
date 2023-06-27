import os
import PySimpleGUI as sg

# grab the resolution of the screen the program is being run on
SCREEN_WIDTH, SCREEN_HEIGHT = sg.Window.get_screen_size()


IMAGE_SAVE_FOLDER = "{}/images".format(os.getcwd())
VIDEO_SAVE_FOLDER = "{}/videos".format(os.getcwd())

RESOLUTION_OPTIONS = ["640 x 480", "1280 x 720", "1920 x 1080", "2560 x 1440"]
