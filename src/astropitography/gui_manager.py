import io
import os
import sys
from typing import Optional, Tuple

import picamera
import PySimpleGUI as sg
from PIL import Image

from astropitography.settings import SCREEN_WIDTH


class GUIManager:
    def __init__(self):
        self.pad_x = 5  # default horizontal padding amount around elements
        self.pad_y = 5  # default vertical padding amount around elements
        self.font_size = 12
        self.GUI_TEXT_SIZE = (int(SCREEN_WIDTH / 85), 1)
        self.window = None

    def create_layout(self, picam_manager):
        """
        This function is responsible for storing the layout of the GUI which is passed to the window object.
        All changes to the layout can be made within this function.

        Parameters
        ----------
        parameters : Class
                    A class of the parameters used within the program. e.g. camera properties, default save locations etc...

        Returns
        -------
        layout     : List[List[Element]]
                    A list containing all the obejcts that are to be displayed in the GUI
        """

        # ------ Menu Definition ------ #
        menu_def = [
            ["Menu", ["Last Image", "Save Location", "Exit"]],
            ["Stacking", ["Stacking Wizard"]],
            ["Date-Time", ["Set Date-Time"]],
        ]

        # define the column layout for the GUI
        image_column = [
            [sg.Image(filename="", key="video")],
        ]

        # controls column 1 holds the camera image settings, e.g. brightness
        controls_column1 = [
            [
                sg.Text(
                    "Brightness",
                    font=("Helvetica", self.font_size, "bold"),
                    size=self.GUI_TEXT_SIZE,
                    pad=(0, self.pad_y),
                ),
                sg.Spin(
                    [i for i in range(0, 100)],
                    initial_value=picam_manager.brightness,
                    font=("Helvetica", 20),
                    key="brightness_slider",
                    pad=(0, self.pad_y),
                ),
            ],
            [
                sg.Text(
                    "Contrast",
                    font=("Helvetica", self.font_size, "bold"),
                    size=self.GUI_TEXT_SIZE,
                ),
                sg.Spin(
                    [i for i in range(-100, 100)],
                    initial_value=picam_manager.contrast,
                    font=("Helvetica", 20),
                    key="contrast_slider",
                    pad=(0, self.pad_y),
                ),
            ],
            [
                sg.Text(
                    "Saturation",
                    font=("Helvetica", self.font_size, "bold"),
                    size=self.GUI_TEXT_SIZE,
                ),
                sg.Spin(
                    [i for i in range(-100, 100)],
                    initial_value=picam_manager.saturation,
                    font=("Helvetica", 20),
                    key="saturation_slider",
                    pad=(0, self.pad_y),
                ),
            ],
            [
                sg.Text(
                    "Sharpness",
                    font=("Helvetica", self.font_size, "bold"),
                    size=self.GUI_TEXT_SIZE,
                ),
                sg.Spin(
                    [i for i in range(0, 100)],
                    initial_value=picam_manager.sharpness,
                    font=("Helvetica", 20),
                    key="sharpness_slider",
                    pad=(0, self.pad_y),
                ),
            ],
        ]

        # controls column 2 holds the other options such as no. of images, shutter speed etc...
        controls_column2 = [
            [
                sg.Text(
                    "Exposure / s",
                    font=("Helvetica", self.font_size, "bold"),
                    size=self.GUI_TEXT_SIZE,
                    pad=(0, self.pad_y),
                ),
                sg.Spin(
                    [i for i in range(0, 200)],
                    initial_value=picam_manager.exposure,
                    font=("Helvetica", 20),
                    key="exposure_slider",
                    pad=(0, self.pad_y),
                ),
            ],
            [
                sg.Text(
                    "Number of images",
                    font=("Helvetica", self.font_size, "bold"),
                    size=self.GUI_TEXT_SIZE,
                    pad=(0, self.pad_y),
                ),
                sg.Spin(
                    [i for i in range(1, 100)],
                    initial_value=picam_manager.img_count,
                    font=("Helvetica", 20),
                    key="no_images_slider",
                    pad=(0, self.pad_y),
                ),
            ],
            [
                sg.Text(
                    "Time step / s",
                    font=("Helvetica", self.font_size, "bold"),
                    size=self.GUI_TEXT_SIZE,
                    pad=(0, self.pad_y),
                ),
                sg.Spin(
                    [i for i in range(0, 100)],
                    initial_value=picam_manager.time_step,
                    font=("Helvetica", 20),
                    key="time_step_slider",
                    pad=(0, self.pad_y),
                ),
            ],
            [
                sg.Text(
                    "Video duration / s",
                    font=("Helvetica", self.font_size, "bold"),
                    size=self.GUI_TEXT_SIZE,
                    pad=(0, self.pad_y),
                ),
                sg.Spin(
                    [i for i in range(1, 100)],
                    initial_value=picam_manager.vid_time,
                    font=("Helvetica", 20),
                    key="video_duration_slider",
                    pad=(0, self.pad_y),
                ),
            ],
        ]

        # controls column 3 holds the large buttons for the program which control image capture etc...
        controls_column3 = [
            [
                sg.Button(
                    "Capture", size=(10, 1), font="Helvetica 14", pad=(0, self.pad_y)
                ),
                sg.Button(
                    "Record",
                    size=(10, 1),
                    font="Helvetica 14",
                    pad=(self.pad_x, self.pad_y),
                ),
            ],
            [
                sg.Button(
                    "- Resize -", size=(10, 1), font="Helvetica 14", pad=(0, self.pad_y)
                ),
                sg.Button(
                    "+ Resize +",
                    size=(10, 1),
                    font="Helvetica 14",
                    pad=(self.pad_x, self.pad_y),
                ),
            ],
            [
                sg.Button(
                    "Crosshair On",
                    size=(10, 1),
                    font="Helvetica 14",
                    pad=(0, self.pad_y),
                ),
                sg.Button(
                    "Crosshair Off",
                    size=(10, 1),
                    font="Helvetica 14",
                    pad=(self.pad_x, self.pad_y),
                ),
            ],
            [
                sg.Button(
                    "Set to Default",
                    size=(10, 1),
                    font="Helvetica 14",
                    pad=(0, self.pad_y),
                ),
                sg.Button(
                    "Where am I?",
                    size=(10, 1),
                    font="Helvetica 14",
                    pad=(self.pad_x, self.pad_y),
                ),
            ],
            [sg.Button("Exit", size=(10, 1), font="Helvetica 14", pad=(0, self.pad_y))],
            [
                sg.Text(
                    "Status:", size=(6, 1), font=("Helvetica", 18), pad=(0, self.pad_y)
                ),
                sg.Text(
                    "Idle",
                    size=(8, 1),
                    font=("Helvetica", 18),
                    text_color="Red",
                    key="status",
                    pad=(0, self.pad_y),
                ),
            ],
        ]

        # controls column 4 holds the options which can be toggled included DNG conversion etc...
        controls_column4 = [
            [
                sg.Text(
                    "Grey scale:",
                    font=("Helvetica", self.font_size, "bold"),
                    pad=(0, self.pad_y),
                ),
                sg.Checkbox(
                    "",
                    size=(int(10), 1),
                    enable_events=True,
                    key="greyscale",
                    pad=(0, self.pad_y),
                ),
            ],
            [
                sg.Text(
                    "Convert to DNG:",
                    font=("Helvetica", self.font_size, "bold"),
                    pad=(0, self.pad_y),
                ),
                sg.Checkbox(
                    "",
                    size=(int(10), 1),
                    enable_events=True,
                    key="convertdng",
                    pad=(0, self.pad_y),
                ),
            ],
            [
                sg.Text(
                    "dark:",
                    font=("Helvetica", self.font_size, "bold"),
                    pad=(0, self.pad_y),
                ),
                sg.Checkbox(
                    "",
                    size=(int(10), 1),
                    enable_events=True,
                    key="dark",
                    pad=(0, self.pad_y),
                ),
                sg.Text(
                    "light:",
                    font=("Helvetica", self.font_size, "bold"),
                    pad=(0, self.pad_y),
                ),
                sg.Checkbox(
                    "",
                    size=(int(10), 1),
                    enable_events=True,
                    key="light",
                    pad=(0, self.pad_y),
                ),
            ],
            [
                sg.Text(
                    "bias:",
                    font=("Helvetica", self.font_size, "bold"),
                    pad=(0, self.pad_y),
                ),
                sg.Checkbox(
                    "",
                    size=(int(10), 1),
                    enable_events=True,
                    key="bias",
                    pad=(0, self.pad_y),
                ),
                sg.Text(
                    "flat:   ",
                    font=("Helvetica", self.font_size, "bold"),
                    pad=(0, self.pad_y),
                ),
                sg.Checkbox(
                    "",
                    size=(int(10), 1),
                    enable_events=True,
                    key="flat",
                    pad=(0, self.pad_y),
                ),
            ],
        ]

        # define the window layout
        layout = [
            [
                sg.Menu(
                    menu_def,
                )
            ],
            [sg.Column(image_column)],
            [sg.Column(controls_column3)],
            [
                sg.Frame(
                    "Settings",
                    layout=[
                        [sg.Column(controls_column4)],
                        [sg.Column(controls_column2)],
                        [sg.HorizontalSeparator()],
                        [sg.Column(controls_column1)],
                    ],
                )
            ],
        ]

        return layout

    def create_window(self, picam_manager) -> None:
        """
        This is the function that builds the GUI window using a supplied layout
        """

        # create a new layout given the GUI settings and default camera settings
        layout = self.create_layout(picam_manager)

        # create invisible window with no layout
        window = sg.Window(
            "AstroPitography",
            [[]],
            location=(1280, 0),
            keep_on_top=False,
            finalize=True,
            resizable=False,
            no_titlebar=False,  # set this to False so popups sit on top of the main window
            auto_size_buttons=True,
            grab_anywhere=False,
        )
        # size=(SCREEN_WIDTH,SCREEN_HEIGHT))

        window.extend_layout(window, layout)

        self.window = window

    def create_image_window(image) -> None:
        """
        This is the function that builds the image window to show the last image

        To view the image it must first be converted and saved as a .png
        Then it is reopened in the image viewier in pysimplegui

        TODO: Improve this functionality without the need to save the image

        Parameters
        ----------
        image : str
                The path and name of the last image captured

        Returns
        -------
        window : Window object
                The GUI window with all specified elements displayed
        """
        # set the default size of the last image and image window
        image_window_size = (640, 480)

        # open the original raw image
        pil_image = Image.open(image)

        # resize the image so it can be previewed and does not cover the entire screen
        resizedImage = pil_image.resize(image_window_size, Image.ANTIALIAS)

        # create a bytes object
        png_bio = io.BytesIO()

        # save the image as a png image
        resizedImage.save(png_bio, format="PNG")

        # create the data which will be displayed in pysimplegui
        png_data = png_bio.getvalue()

        # create the window and show the converted last image taken
        layout = [
            [sg.Image(data=png_data, size=image_window_size)],
            [
                sg.Button(
                    "Delete", font=("Helvetica", 10), size=(int(SCREEN_WIDTH / 90), 1)
                ),
                sg.Button(
                    "Return",
                    font=("Helvetica", 10),
                    size=(int(SCREEN_WIDTH / 90), 1),
                    pad=(5, 0),
                ),
            ],
        ]

        # give the window a title
        window = sg.Window("Last Image", layout, location=(1280, 0))

    def _pad(resolution: Tuple, width: int = 32, height: int = 16) -> Tuple[Tuple[int]]:
        """
        Pads the specified resolution up to the nearest multiple of *width* and *height*
        this is needed because overlays require padding to the camera's block size (32x16)

        Parameters
        ----------
        resolution : tuple
                    The size of the image to be overlayed on the live preview

        width  : int
                The default width

        height : int
                The default height

        Returns
        -------
        resolution_tuple : tuple
                        Tuple containing correctly scaled width and height of the overlay image to use with the live preview
        """

        return (
            ((resolution[0] + (width - 1)) // width) * width,
            ((resolution[1] + (height - 1)) // height) * height,
        )

    def remove_overlays(camera) -> None:
        """
        Removes any overlays currently being displayed on the live preview

        Parameters
        ----------
        camera : picamera.camera.PiCamera
                The picamera camera object
        """
        # remove all overlays from the camera preview
        for overlay in camera.overlays:
            camera.remove_overlay(overlay)

    def preview_overlay(camera: Optional[picamera.camera.PiCamera]=None, resolution: Optional[Tuple]=None, overlay: Image.Image=None) -> None:
        """
        This function actually overlays the image on the live preview

        Parameters
        ----------
        camera     : picamera.camera.PiCamera
                    The picamera camera object

        resolution : tuple
                    The width and height of the window containing the overlay image

        overlay    : PIL.Image.Image
                    The overlay image object

        Returns
        -------
        None
        """
        # remove all overlays
        remove_overlays(camera)

        # pad it to the right resolution
        pad = Image.new("RGBA", self._pad(overlay.size))
        pad.paste(overlay, (0, 0), overlay)

        # add the overlay
        overlay = camera.add_overlay(pad.tobytes(), size=overlay.size)
        overlay.fullscreen = False
        overlay.window = (0, 0, resolution[0], resolution[1])
        overlay.alpha = 128
        overlay.layer = 3
