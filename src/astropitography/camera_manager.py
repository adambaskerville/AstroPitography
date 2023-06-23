import os

from pidng.core import RPICAM2DNG

from settings import SCREEN_HEIGHT


class PiCam:
    def __init__(self):
        # default values for the camera
        self.brightness = 50
        self.contrast = 0
        self.saturation = 0
        self.sharpness = 0
        self.image_no = 1
        self.exposure = 1
        self.time_step = 2
        self.vid_time = 10
        self.image_size = (int(SCREEN_HEIGHT / 2), int(SCREEN_HEIGHT / 2))
        self.preview_size = (int(SCREEN_HEIGHT / 2), int(SCREEN_HEIGHT / 2))
        self.save_folder = "{}/images".format(os.getcwd())
        self.save_folder_vid = "{}/videos".format(os.getcwd())
        self.last_image = (
            "blackimage.png"  # black frame to fill the last image menu popout
        )

        # other options
        self.DNG_convert = False  # default flag for image DNG conversion
        self.delete_JPG_twin = False

    def convert_to_DNG(self, image_name):
        """
        This function will crate a DNG image from the .jpg + .raw data using PiDNG

        Parameters
        ----------
        image_save_file_name : str
                            a string filename

        Returns
        -------
        None
        """
        # call RPICAM2DNG from PiDNG
        raw_dng_convert = RPICAM2DNG()

        # convert the image to DNG format
        raw_dng_convert.convert(image_name)

        # remove the original jpg image to save space
        if self.delete_JPG_twin:
            os.remove(image_name + ".jpg")


main_picam = PiCam()
