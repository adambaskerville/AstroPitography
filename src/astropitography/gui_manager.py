import PySimpleGUI as sg

from settings import SCREEN_WIDTH
from camera_manager import main_picam


class GUISettings:
    def __init__(self):
        self.pad_x = 5  # default horizontal padding amount around elements
        self.pad_y = 5  # default vertical padding amount around elements
        self.font_size = 12  # font size for text elements in the GUI
        self.GUI_TEXT_SIZE = (int(SCREEN_WIDTH / 85), 1)  # default size for text elem

    def create_layout(self):
        """
        This function is responsible for storing the layout of the GUI which is passed to the window object. All changes to the layout can be made within this function

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
                    initial_value=p.default_brightness,
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
                    initial_value=main_picam.contrast,
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
                    initial_value=self.default_saturation,
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
                    initial_value=main_picam.sharpness,
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
                    initial_value=main_picam.exposure,
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
                    initial_value=main_picam.image_no,
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
                    initial_value=main_picam.time_step,
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
                    initial_value=main_picam.vid_time,
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
                    "Capture", size=(10, 1), font="Helvetica 14", pad=(0, p.pad_y)
                ),
                sg.Button(
                    "Record", size=(10, 1), font="Helvetica 14", pad=(p.pad_x, p.pad_y)
                ),
            ],
            [
                sg.Button(
                    "- Resize -", size=(10, 1), font="Helvetica 14", pad=(0, p.pad_y)
                ),
                sg.Button(
                    "+ Resize +",
                    size=(10, 1),
                    font="Helvetica 14",
                    pad=(p.pad_x, p.pad_y),
                ),
            ],
            [
                sg.Button(
                    "Crosshair On", size=(10, 1), font="Helvetica 14", pad=(0, p.pad_y)
                ),
                sg.Button(
                    "Crosshair Off",
                    size=(10, 1),
                    font="Helvetica 14",
                    pad=(p.pad_x, p.pad_y),
                ),
            ],
            [
                sg.Button(
                    "Defaults", size=(10, 1), font="Helvetica 14", pad=(0, p.pad_y)
                ),
                sg.Button(
                    "Where am I?",
                    size=(10, 1),
                    font="Helvetica 14",
                    pad=(p.pad_x, p.pad_y),
                ),
            ],
            [sg.Button("Exit", size=(10, 1), font="Helvetica 14", pad=(0, p.pad_y))],
            [
                sg.Text(
                    "Status:", size=(6, 1), font=("Helvetica", 18), pad=(0, p.pad_y)
                ),
                sg.Text(
                    "Idle",
                    size=(8, 1),
                    font=("Helvetica", 18),
                    text_color="Red",
                    key="output",
                    pad=(0, p.pad_y),
                ),
            ],
        ]

        # controls column 4 holds the options which can be toggled included DNG conversion etc...
        controls_column4 = [
            [
                sg.Text(
                    "Grey scale:",
                    font=("Helvetica", p.font_size, "bold"),
                    pad=(0, p.pad_y),
                ),
                sg.Checkbox(
                    "",
                    size=(int(10), 1),
                    enable_events=True,
                    key="greyscale",
                    pad=(0, p.pad_y),
                ),
            ],
            [
                sg.Text(
                    "Convert to DNG:",
                    font=("Helvetica", p.font_size, "bold"),
                    pad=(0, p.pad_y),
                ),
                sg.Checkbox(
                    "",
                    size=(int(10), 1),
                    enable_events=True,
                    key="convertdng",
                    pad=(0, p.pad_y),
                ),
            ],
            [
                sg.Text(
                    "dark:", font=("Helvetica", p.font_size, "bold"), pad=(0, p.pad_y)
                ),
                sg.Checkbox(
                    "",
                    size=(int(10), 1),
                    enable_events=True,
                    key="dark",
                    pad=(0, p.pad_y),
                ),
                sg.Text(
                    "light:", font=("Helvetica", p.font_size, "bold"), pad=(0, p.pad_y)
                ),
                sg.Checkbox(
                    "",
                    size=(int(10), 1),
                    enable_events=True,
                    key="light",
                    pad=(0, p.pad_y),
                ),
            ],
            [
                sg.Text(
                    "bias:", font=("Helvetica", p.font_size, "bold"), pad=(0, p.pad_y)
                ),
                sg.Checkbox(
                    "",
                    size=(int(10), 1),
                    enable_events=True,
                    key="bias",
                    pad=(0, p.pad_y),
                ),
                sg.Text(
                    "flat:   ",
                    font=("Helvetica", p.font_size, "bold"),
                    pad=(0, p.pad_y),
                ),
                sg.Checkbox(
                    "",
                    size=(int(10), 1),
                    enable_events=True,
                    key="flat",
                    pad=(0, p.pad_y),
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
