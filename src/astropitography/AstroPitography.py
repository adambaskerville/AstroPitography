import os
from sys import intern
import time
from pathlib import Path
from typing import List, Tuple, Union

import picamera
import PySimpleGUI as sg
from PIL import Image

import astropitography.utils as utils
import astropitography.settings as config
from astropitography.tetra3 import Tetra3
from astropitography.camera_manager import PiCamManager
from astropitography.gui_manager import GUIManager

def run() -> None:
    """
    This is the main function that controls the entire program. It has all been wrapped 
    inside a function for easy exit of the various options using a function return

    It has no explicit inputs or returns. Its main purpose is to allow the while loop to
    run and for pysimplegui to keep the window open whilst showing a live feed of what 
    the camera is seeing.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    # create instance and load default_database (built with max_fov=12 and the rest as default)
    t3 = Tetra3("db/default_database")

    gui_manager = GUIManager()
    picam_manager = PiCamManager()

    # creates the GUI window using create_window
    gui_manager.create_window(picam_manager)

    # set the default save folder for the images
    img_save_directory: str = config.IMAGE_SAVE_FOLDER

    # if images folder does not exist, create it
    if not os.path.isdir(img_save_directory):
        os.mkdir(img_save_directory)

    # set the default save folder for the videos
    vid_save_directory: str = config.VIDEO_SAVE_FOLDER

    # if videos folder does not exist, create it
    if not os.path.isdir(vid_save_directory):
        os.mkdir(vid_save_directory)

    preview_width, preview_height = picam_manager.preview_size
    
    # start the preview
    with picamera.PiCamera(resolution=(3280, 2464)) as camera:
        picam_manager.camera = camera
        camera.start_preview(
            resolution=(1440, 1080), fullscreen=False, window=(0, 0, preview_width, preview_height)
        )
        time.sleep(1)


        while True:
            # setup the events and values which the GUI will call and modify
            gui_manager.window, event, values = sg.read_all_windows(timeout=0)

            # set the date-time if specified
            if event == "Set Date-Time":
                utils.set_date_time()

            # run the plate solver
            if event == "Where am I?":
                utils.plate_solver(t3, picam_manager.last_image)
                # plate_solver(t3, "tetra3/test_data/2019-07-29T204726_Alt60_Azi45_Try1.tiff")

            # run the image stacking capability
            # if event == "Stacking Wizard":
            #     images = utils.image_stacking()

            # change the default save location if selected from the Menu
            if event == "Save Location":
                img_save_directory = sg.PopupGetFolder(
                    "save_folder",
                    initial_folder="{}".format(config.IMAGE_SAVE_FOLDER),
                    no_window=True,
                    keep_on_top=True,
                )

            # if the user selects the last image option
            if event == "Last Image":
                gui_manager.create_image_window(picam_manager.last_image)

            if values["convertdng"]:
                picam_manager.DNG_convert = True

            # declare the camera settings if they have been changed
            picam_manager.update_camera_settings(values)

            # closing the program by pressing exit
            if event == sg.WIN_CLOSED or event == "Exit":
                # stop the live preview
                camera.stop_preview()
                # close the camera
                camera.close()
                # close the GUI window
                gui_manager.window.close()
                
                return

            if event == "Crosshair On":
                img = Image.open(Path(__file__).parent / "crosshair.png").convert(
                    "RGBA"
                )
                gui_manager.preview_overlay(camera=camera, resolution=(preview_width, preview_height), overlay=img)

            if event == "Crosshair Off":
                gui_manager.remove_overlays(camera)

            # record video
            if event == "Record":
                picam_manager.capture_video(gui_manager, vid_save_directory)

            # capture image
            if event == "Capture":
                picam_manager.capture_image(gui_manager, values, img_save_directory)

            # reset the camera settings to the default values
            if event == "Set to Defaults":
                picam_manager.reset_to_default()

                gui_manager.window["brightness_slider"].update(picam_manager.brightness)
                gui_manager.window["contrast_slider"].update(picam_manager.contrast)
                gui_manager.window["saturation_slider"].update(picam_manager.saturation)
                gui_manager.window["sharpness_slider"].update(picam_manager.sharpness)
                gui_manager.window["exposure_slider"].update(picam_manager.exposure)
                gui_manager.window["no_images_slider"].update(picam_manager.img_count)
                gui_manager.window["time_step_slider"].update(picam_manager.time_step)
                gui_manager.window["video_duration_slider"].update(
                    picam_manager.vid_time
                )
