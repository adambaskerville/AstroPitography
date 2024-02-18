import os
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Union, Tuple
import picamera
from pidng.core import RPICAM2DNG

from astropitography.settings import SCREEN_HEIGHT


class PiCamManager:
    def __init__(self):
        """
        Initialize the PiCamManager instance with default values
        """
        self.camera: Optional[picamera.PiCamera] = None


        # default values for the camera
        self.brightness: int = 50
        self.contrast: int = 0
        self.saturation: int = 0
        self.sharpness: int = 0
        self.img_count: int = 1  # num of images to use for multiple exposures
        self.exposure: int = 1
        self.time_step: int = 2
        self.vid_time: int = 10
        self.image_size: Tuple[int, int] = (int(SCREEN_HEIGHT / 2), int(SCREEN_HEIGHT / 2))
        self.preview_size: Tuple[int, int] = (int(SCREEN_HEIGHT / 2), int(SCREEN_HEIGHT / 2))
        self.last_image: Path = Path(__file__).parent / "blackimage.png"
        self.default_settings = {
            "brightness": 50,
            "contrast": 0,
            "saturation": 0,
            "sharpness": 0,
            "image_no": 1,
            "exposure": 1,
            "time_step": 2,
            "vid_time": 10,
        }

        self.DNG_convert : bool = False  # default flag for image DNG conversion
        self.delete_JPG_twin : bool = False

    # fmt: off
    def update_camera_settings(self, values: dict) -> None:
        """
        Update camera settings based on user input values

        Parameters:
            - values (dict): A dictionary containing user input values from the GUI
        """
        self.brightness = int(values["brightness_slider"])  # Grabs the user set brightness value
        self.contrast = int(values["contrast_slider"])  # Grabs the user set contrast value
        self.saturation = int(values["saturation_slider"])  # Grabs the user set saturation value
        self.sharpness = int(values["sharpness_slider"])  # Grabs the user set sharpness value
        self.exposure = int(values["exposure_slider"])  # Grabs the user set exposure value
        self.exposure_img_count = int(values["no_images_slider"])  # Grabs the user set number of images to be taken
        self.time_step = int(values["time_step_slider"])  # Grabs the user set time increment between images
        self.vid_time = values["video_duration_slider"]  # Grabs the user set video length

        if self.camera is not None:
            # apply the new settings to the camera
            self.camera.brightness = self.brightness  # brightness     min: 0   , max: 255 , increment:1
            self.camera.contrast = self.contrast      # contrast       min: 0   , max: 255 , increment:1
            self.camera.saturation = self.saturation  # saturation     min: 0   , max: 255 , increment:1
            self.camera.sharpness = self.sharpness    # sharpness      min: 0   , max: 255 , increment:1


    def capture_video(self, gui_manager, save_location: str) -> None:
        """
        Capture a video using the camera and save it to the specified location

        Parameters:
            - gui_manager (GUIManager): The GUI manager instance
            - save_location (str): The location to save the video
        """
        # datetime object containing current date and time for time stamping the images and videos
        now = datetime.now()

        # dd/mm/YY H_M_S
        # note colons were removed as the RPi file system disliked moving files with colons in their name
        curr_date_time = now.strftime("%d_%m_%Y_%H_%M_%S")

        window = gui_manager.window
        picam = self.camera

        # update the activity notification
        window["status"].update("Working...")
        window.Refresh()

        # specify the name of the video save file
        video_file = f"{save_location}/astropito_video_{curr_date_time}_{self.vid_time}s.yuv"

        # update the activity notification
        window["status"].update("Working...")

        # set the resolution for the video capture
        picam.resolution = (3296, 2464)

        # start the video recording.
        # we use yuv format
        picam.start_recording(video_file, format="yuv")
        picam.wait_recording(self.vid_time)
        picam.stop_recording()

        # reset the activity notification
        window["status"].update("Idle")
        window.Refresh()

    # fmt: off
    def capture_image(self, gui_manager, values: dict, save_location: str) -> None:
        """
        Capture an image using the camera and save it to the specified location

        Parameters:
            - gui_manager (GUIManager): The GUI manager instance
            - values (dict): A dictionary containing user input values from the GUI
            - save_location (str): The location to save the image
        """
        # datetime object containing current date and time for time stamping the images and videos
        now = datetime.now()

        # dd/mm/YY H_M_S
        # note colons were removed as the RPi file system disliked moving files with colons in their name
        curr_date_time = now.strftime("%d_%m_%Y_%H_%M_%S")

        picam = self.camera
        
        # update the activity notification
        gui_manager.window["status"].update("Working...")
        gui_manager.window.Refresh()

        # turn on the grey scale option if it is toggled
        if values["greyscale"]:
            picam.color_effects = (128, 128)
        else:
            picam.color_effects = None

        # check if the dark, light, flat or bias options are selected
        # if they are then specify an append to the image filename
        file_append = ""
        if values["dark"]:
            file_append = file_append + "_dark"
        if values["light"]:
            file_append = file_append + "_light"
        if values["flat"]:
            file_append = file_append + "_flat"
        if values["bias"]:
            file_append = file_append + "_bias"

        # triggers long exposure
        if self.exposure > 1:
            # triggers multiple long exposures
            for i in range(self.img_count):
                # change the framerate of the camera
                picam.framerate = 1 / self.exposure

                # convert the exposure time in seconds to microseconds
                picam.shutter_speed = int(self.exposure * 1e6)

                # set the camera ISO to 800
                picam.iso = 800

                # give camera a long time to set gains and
                # measure AWB (we may wish to use fixed AWB instead)
                time.sleep(30)
                picam.exposure_mode = "off"

                # automate the name of the file save name
                image_file = f"{save_location}/astropito_image_{curr_date_time}_no-{i}_LE_{self.exposure}s{file_append}.jpeg"
  
                # capture the image in RAW format
                picam.capture(image_file, format="jpeg", bayer=True)

                # if specified convert the jpeg image to a DNG image
                if self.DNG_convert:
                    self.convert_to_DNG(image_file)

            # reset the framerate for the live preview
            picam.framerate = 30

            # reset the camera exposure mode to auto
            picam.exposure_mode = "auto"
        # triggers multiple exposures
        else:
            for i in range(self.img_count):
                # specify image file name
                image_file = f"{save_location}/astropito_image_{curr_date_time}_no-{i}{file_append}.jpeg"

                # capture the image in RAW format
                picam.capture(image_file, format="jpeg", bayer=True)

                # this creates the time gap between images being taken using the value set by the user
                time.sleep(self.time_step)

                # if specified convert the jpeg image to a DNG image
                if self.DNG_convert:
                    self.convert_to_DNG(image_file)

        # set the default last image to be shown. blackimage.png
        self.last_image = image_file

        # reset the activity notification
        gui_manager.window["status"].update("Idle")
        gui_manager.window.Refresh()
    # fmt: on

    def convert_to_DNG(self, image_name: str) -> None:
        """
        Convert a captured image to DNG format.

        Parameters:
            - image_name (str): The name of the image file to convert.
        """
        # call RPICAM2DNG from PiDNG
        raw_dng_convert = RPICAM2DNG()

        # convert the image to DNG format
        raw_dng_convert.convert(image_name)

        # remove the original jpg image to save space
        if self.delete_JPG_twin:
            os.remove(image_name + ".jpg")

    def reset_to_default(self) -> None:
        for attr, value in self.default_settings.items():
            setattr(self, attr, value)

        # apply the default settings to the camera
        # fmt: off
        if self.camera is not None:
            self.camera.brightness = self.brightness  # brightness     min: 0   , max: 255 , increment:1
            self.camera.contrast = self.contrast      # contrast       min: 0   , max: 255 , increment:1
            self.camera.saturation = self.saturation  # saturation     min: 0   , max: 255 , increment:1
            self.camera.sharpness = self.sharpness    # sharpness      min: 0   , max: 255 , increment:1
        # fmt: on
