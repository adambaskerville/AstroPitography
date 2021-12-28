#! /usr/bin/python3 
'''
    Name    : AstroPitography
    Author  : Dr Adam Luke Baskerville
    Date    : 27-Dec-2021
    Version : 1-05
    
    Description
    -----------
    This program provides a simple user interface to control the raspberry pi HQ camera for use in astrophotography.
    
    A variety of camera settings can be controlled including:
    
    * Brightness
    * Contrast
    * Saturation
    * Sharpness
    * Exposure (shutter speed in this instance)
    * Time delay between images
    
    It is currently able to do the following:
    
    * Show a live preview of the camera view; useful for making sure something is in frame
    * Allows for capturing of single images, multiple images with time delay and long exposure imaging
    * When a picture is taken it will be viewable by clicking the 'Menu' button and clicking 'Last Image'
        * if it is a poor quality image it can be deleted by clicking 'Delete'
    * The default save location can also be selected from within the window
        * handy for saving to USB stick etc... especially for large RAW files
    * Video capturing of specified length
    * The image format is RAW, preferred over .png so no information is lost/processed

    Auto Start
    ----------
    If you want the program to start on startup add this to the bottom of .bashrc:
    
    python3 /home/pi/AstroPitography/AstroPitography.py
    
    Dependencies
    ------------
    picamera == 1.13
    pidng == 3.4.7
    Pillow == 8.4.0
    PySimpleGUI == 4.55.1
'''
import os
import sys
import io
import time
import PySimpleGUI as sg
from PIL import Image
from time import sleep
import picamera
from pidng.core import RPICAM2DNG
from datetime import datetime
from tetra3 import Tetra3
from pathlib import Path

# get the home directory
home = str(Path.home())

# set the GUI theme
sg.theme('DarkBlack')

# set the size of the padding around elements
sg.SetOptions(element_padding=(0, 0),
              text_color = 'Red',
              input_text_color ='Red',
              button_color = ('Black', 'Red')) 

# grab the resolution of the screen the program is being run on
SCREEN_WIDTH, SCREEN_HEIGHT = sg.Window.get_screen_size()

# put all key parameters in their own class, Parameters
class Parameters:
    # default image settings
    default_brightness      = 50
    default_contrast        = 0 
    default_saturation      = 0
    default_sharpness       = 0
    default_image_no        = 1
    default_exposure        = 1
    default_time_step       = 2
    default_vid_time        = 10
    default_image_size      = (int(SCREEN_HEIGHT/2), int(SCREEN_HEIGHT/2))
    default_preview_size    = (int(SCREEN_HEIGHT/2), int(SCREEN_HEIGHT/2))
    default_save_folder     = "{}/images".format(os.getcwd())
    default_save_folder_vid = "{}/videos".format(os.getcwd())
    default_last_image      = "blackimage.png" # black frame to fill the last image menu popout
    # other options
    DNG_convert             = False # default flag for image DNG conversion
    pad_x                   = 5     # default horizontal padding amount around elements
    pad_y                   = 5     # default vertical padding amount around elements
    font_size               = 12    # font size for text elements in the GUI
    GUI_TEXT_SIZE           = (int(SCREEN_WIDTH/85), 1) # default size for text elements
    
def convert_to_DNG(image_save_file_name):
    '''
    This function will crate a DNG image from the .jpg + .raw data using PiDNG

    Parameters
    ----------
    image_save_file_name : str
                           a string filename

    Returns
    -------
    None
    '''
    # call RPICAM2DNG from PiDNG
    raw_dng_convert = RPICAM2DNG()

    # convert the image to DNG format 
    raw_dng_convert.convert(image_save_file_name)

    # remove the original jpg image to save space
    #os.remove(image_save_file_name)

def create_layout(parameters):
    '''
    This function is responsible for storing the layout of the GUI which is passed to the window object. All changes to the layout can be made within this function

    Parameters
    ----------
    parameters : Class
                 A class of the parameters used within the program. e.g. camera properties, default save locations etc...

    Returns
    -------
    layout     : List[List[Element]]
                 A list containing all the obejcts that are to be displayed in the GUI
    '''
    # assign the parameters to name p for ease of use
    p=parameters

    # ------ Menu Definition ------ #      
    menu_def = [['Menu', ['Last Image', 'Save Location', 'Exit']],
                ['Stacking', ['Stacking Wizard']],
                ['Date-Time',['Set Date-Time']]]     

    # define the column layout for the GUI
    image_column = [
        [sg.Image(filename='', key='video')],
    ]

    # controls column 1 holds the camera image settings, e.g. brightness
    controls_column1 = [
        [sg.Text('Brightness', font=("Helvetica", p.font_size, "bold"), size=p.GUI_TEXT_SIZE, pad=(0,p.pad_y)),                
         sg.Spin([i for i in range(0, 100)], initial_value=p.default_brightness, font=('Helvetica', 20), key='brightness_slider', pad=(0,p.pad_y))],
        [sg.Text('Contrast', font=("Helvetica", p.font_size, "bold"), size=p.GUI_TEXT_SIZE),      
         sg.Spin([i for i in range(-100, 100)], initial_value=p.default_contrast, font=('Helvetica', 20), key='contrast_slider', pad=(0,p.pad_y))],
        [sg.Text('Saturation', font=("Helvetica", p.font_size, "bold"), size=p.GUI_TEXT_SIZE),               
         sg.Spin([i for i in range(-100, 100)], initial_value=p.default_saturation, font=('Helvetica', 20), key='saturation_slider', pad=(0,p.pad_y))],
        [sg.Text('Sharpness', font=("Helvetica", p.font_size, "bold"), size=p.GUI_TEXT_SIZE),               
         sg.Spin([i for i in range(0, 100)], initial_value=p.default_sharpness, font=('Helvetica', 20), key='sharpness_slider', pad=(0,p.pad_y))], 
    ]

    # controls column 2 holds the other options such as no. of images, shutter speed etc...
    controls_column2 = [
        [sg.Text('Exposure / s', font=("Helvetica", p.font_size, "bold"), size=p.GUI_TEXT_SIZE, pad=(0,p.pad_y)),               
         sg.Spin([i for i in range(0, 200)], initial_value=p.default_exposure, font=('Helvetica', 20), key='exposure_slider', pad=(0,p.pad_y))],
        [sg.Text('Number of images', font=("Helvetica", p.font_size, "bold"), size=p.GUI_TEXT_SIZE, pad=(0,p.pad_y)),               
         sg.Spin([i for i in range(1, 100)], initial_value=p.default_image_no, font=('Helvetica', 20), key='no_images_slider', pad=(0,p.pad_y))],
        [sg.Text('Time step / s', font=("Helvetica", p.font_size, "bold"), size=p.GUI_TEXT_SIZE, pad=(0,p.pad_y)),               
         sg.Spin([i for i in range(0, 100)], initial_value=p.default_time_step, font=('Helvetica', 20), key='time_step_slider', pad=(0,p.pad_y))],
        [sg.Text('Video duration / s', font=("Helvetica", p.font_size, "bold"), size=p.GUI_TEXT_SIZE, pad=(0,p.pad_y)),               
         sg.Spin([i for i in range(1, 100)], initial_value=p.default_vid_time, font=('Helvetica', 20), key='video_duration_slider', pad=(0,p.pad_y))], 
    ]

    # controls column 3 holds the large buttons for the program which control image capture etc...
    controls_column3 = [
        [sg.Button('Capture', size=(10, 1), font='Helvetica 14', pad=(0,p.pad_y)),
         sg.Button('Record', size=(10, 1), font='Helvetica 14', pad=(p.pad_x,p.pad_y))],
        [sg.Button('- Resize -', size=(10, 1), font='Helvetica 14', pad=(0,p.pad_y)),
         sg.Button('+ Resize +', size=(10, 1), font='Helvetica 14', pad=(p.pad_x,p.pad_y)),
         ],
        [sg.Button('Crosshair On', size=(10, 1), font='Helvetica 14', pad=(0,p.pad_y)),
         sg.Button('Crosshair Off', size=(10, 1), font='Helvetica 14', pad=(p.pad_x,p.pad_y)),
         ],
        [sg.Button('Defaults', size=(10, 1), font='Helvetica 14', pad=(0,p.pad_y)),
         sg.Button('Where am I?', size=(10, 1), font='Helvetica 14', pad=(p.pad_x,p.pad_y))],
        [sg.Button('Exit', size=(10, 1), font='Helvetica 14', pad=(0,p.pad_y))],
        [sg.Text('Status:', size=(6,1), font=('Helvetica', 18), pad=(0,p.pad_y)),
         sg.Text('Idle', size=(8, 1), font=('Helvetica', 18), text_color='Red', key='output', pad=(0,p.pad_y))],
    ]

    # controls column 4 holds the options which can be toggled included DNG conversion etc...
    controls_column4 = [
        [sg.Text('Grey scale:', font=("Helvetica", p.font_size, "bold"), pad=(0,p.pad_y)),
         sg.Checkbox('', size=(int(10), 1), enable_events=True, key='greyscale', pad=(0,p.pad_y))],
        [sg.Text('Convert to DNG:', font=("Helvetica", p.font_size, "bold"), pad=(0,p.pad_y)),
         sg.Checkbox('', size=(int(10), 1), enable_events=True, key='convertdng', pad=(0,p.pad_y))],
        [sg.Text('dark:', font=("Helvetica", p.font_size, "bold"), pad=(0,p.pad_y)),
         sg.Checkbox('', size=(int(10), 1), enable_events=True, key='dark', pad=(0,p.pad_y)),
         sg.Text('light:', font=("Helvetica", p.font_size, "bold"), pad=(0,p.pad_y)),
         sg.Checkbox('', size=(int(10), 1), enable_events=True, key='light', pad=(0,p.pad_y))],
        [sg.Text('bias:', font=("Helvetica", p.font_size, "bold"), pad=(0,p.pad_y)),
         sg.Checkbox('', size=(int(10), 1), enable_events=True, key='bias', pad=(0,p.pad_y)),
         sg.Text('flat:   ', font=("Helvetica", p.font_size, "bold"), pad=(0,p.pad_y)),
         sg.Checkbox('', size=(int(10), 1), enable_events=True, key='flat', pad=(0,p.pad_y))],
    ]

    # define the window layout
    layout = [[sg.Menu(menu_def, )],
              [sg.Column(image_column)],
              [sg.Column(controls_column3)],
              [sg.Frame("Settings", layout=[[sg.Column(controls_column4)], 
                                            [sg.Column(controls_column2)],
                                            [sg.HorizontalSeparator()],
                                            [sg.Column(controls_column1)],
                                            ])],
              ]

    return layout

def create_window(layout):
    '''
    This is the function that builds the GUI window using a supplied layout

    Parameters
    ----------
    layout : List[List[Element]]
             A list containing all the objects that are to be displayed in the GUI

    Returns
    -------
    window : Window object
             The GUI window with al lspecified elements displayed
    '''
    # create invisible window with no layout
    window = sg.Window('AstroPitography', [[]], location=(1280,0), 
                                                keep_on_top=False, 
                                                finalize=True, 
                                                resizable=False, 
                                                no_titlebar=False, # set this to False so popups sit on top of the main window
                                                auto_size_buttons=True, 
                                                grab_anywhere=False)
                                                #size=(SCREEN_WIDTH,SCREEN_HEIGHT))

    window.extend_layout(window, layout)

    return window

def create_image_window(image):
    '''
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
    '''
    # set the default size of the last image and image window
    image_window_size = (640,480)
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
    layout = [[sg.Image(data=png_data, size=image_window_size)],
              [sg.Button('Delete', font=("Helvetica", 10), size=(int(SCREEN_WIDTH/90), 1)),
               sg.Button('Return', font=("Helvetica", 10), size=(int(SCREEN_WIDTH/90), 1), pad=(5,0))]]
    
    # give the window a title
    window = sg.Window("Last Image", layout, location=(1280,0))

    while True:
        event, values = window.read()
        # if the Delete button is pressed, then delete the last image taken
        if event == 'Delete':
            try:
                if Parameters.default_last_image in ["blackimage.png"]:
                    # if the default image is still the default black image then pass
                    pass
                else:
                    # if the default image is a new image which is not required then delete it
                    os.remove(Parameters.default_last_image)
                    Parameters.default_last_image = "blackimage.png"
            except:
                print("File not found, continuing.")
                pass
        elif event == "Return" or event == sg.WIN_CLOSED:
            break
        
    window.close()

def _pad(resolution, width=32, height=16):
    '''
    pads the specified resolution up to the nearest multiple of *width* and *height*
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

    '''
    
    return (
        ((resolution[0] + (width - 1)) // width) * width,
        ((resolution[1] + (height - 1)) // height) * height,
    )

def remove_overlays(camera):
    '''
    This function removes any overlays currently being displayed on the live preview
    
    Parameters
    ----------
    camera : picamera.camera.PiCamera
             The picamera camera object
    
    Returns
    -------
    None
    '''
    # remove all overlays from the camera preview
    for o in camera.overlays:
        camera.remove_overlay(o)

def preview_overlay(camera=None, resolution=None, overlay=None):
    '''
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
    '''
    # remove all overlays
    remove_overlays(camera)
    
    # pad it to the right resolution
    pad = Image.new('RGBA', _pad(overlay.size))
    pad.paste(overlay, (0, 0), overlay)
    
    # add the overlay
    overlay = camera.add_overlay(pad.tobytes(), size=overlay.size)
    overlay.fullscreen = False
    overlay.window = (0, 0, resolution[0], resolution[1])
    overlay.alpha = 128
    overlay.layer = 3

def folder_file_selecter():
    '''
    This function offers a popup menu allowing for multiple images to be selected
    
    It views a file and file tree
    
    Note, if scanning a large folder then tkinter will eventually complain about too many bitmaps.
    
    This can be fixed by reusing the images within PySimpleGUI (TODO: implement if needed at some point)
    
    Parameters
    ----------
    
    Returns
    -------
    values :
    
    '''
    # base64 versions of images of a folder and a file. PNG files (may not work with PySimpleGUI27, swap with GIFs)
    folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
    file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'

    # create popup which lets user select folder with images
    starting_path = sg.popup_get_folder('Select Folder to display')

    if not starting_path:
        sys.exit(0)

    treedata = sg.TreeData()

    def add_files_in_folder(parent, dirname):
        '''
        This builds the file tree by looping through the selected folder
        
        Parameters
        ----------
        parent  : 
        
        dirname : str
                  The directory where the images are located 
        Returns
        -------
        None
        '''
        files = os.listdir(dirname)
        for f in files:
            fullname = os.path.join(dirname, f)
            if os.path.isdir(fullname): # if it's a folder, add folder and recurse
                treedata.Insert(parent, fullname, f, values=[], icon=folder_icon)
                add_files_in_folder(fullname, fullname)
            else:
                treedata.Insert(parent, fullname, f, values=[os.stat(fullname).st_size], icon=file_icon)

    add_files_in_folder('', starting_path)

    layout = [[sg.Text('Select images to stack')],
              [sg.Tree(data=treedata,
                       headings=['Size', ],
                       auto_size_columns=True,
                       select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                       num_rows=20,
                       col0_width=40,
                       key='-TREE-',
                       show_expanded=False,
                       enable_events=True,
                       ),],
              [sg.Button('Ok'), sg.Button('Cancel')]]

    window = sg.Window('Image tree', layout, resizable=True, finalize=True)
    window['-TREE-'].expand(True, True) # resize with the window (Full support for Tree element being released in 4.44.0)

    while True: # Event Loop
        event, images = window.read()
        if event in (sg.WIN_CLOSED, 'Cancel', 'Ok'):
            break
        
    window.close()
    return images['-TREE-']

def set_date_time():
    '''
    This function allows for the time and date to be set on the raspberry pi from within the GUI
    For headless RPi setups this is very useful as it cannot use NTP time synchronisation with no WiFi
    
    It simply takes user input for the date and time and runs a shell command using the os module: 'sudo date -s date_time'
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    '''
    # popup window to input date and time
    date_time = sg.popup_get_text("Set Raspberry Pi Date and Time. Format: yyyy-mm-dd hh:mm:ss", "Input date and time", text_color='White')

    # run the command
    os.system('sudo date -s "{}"'.format(date_time))
    
def image_stacking():
    '''
    This function controls image stacking (averaging)
    It opens up a seperate window where images can be selected
    It then
    
    Parameters
    ----------
    
    Returns
    -------
    
    '''
    # open up 
    images = folder_file_selecter()
    
    return images

def plate_solver(star_database, impath):
    '''
    This function allows for plate solving functionality
    It takes the last image taken and compares it against a stellar database using tetra3
    tetra3 is published by the ESA: https://tetra3.readthedocs.io/en/latest/index.html
    It is licensed under the Apache License, Version 2.0
    
    Parameters
    ----------
    star_database :
    
    impath        : str
                    The path of the image to be plate solved    
    
    Returns
    -------
    None
    '''
    print('Solving for image at: ' + str(impath))
    with Image.open(str(impath)) as img:
        solved = star_database.solve_from_image(img)  # Adding e.g. fov_estimate=11.4, fov_max_error=.1 improves performance
    
    try:
        sg.popup_ok("Right Ascension (RA) = {:.6f}\nDeclination (DEL) = {:.6f}\nRoll = {:.6f}\nField Of View = {:.3f}\nMatches = {}".format(solved["RA"],
                                                                                                                                 solved["Dec"],
                                                                                                                                 solved["Roll"],
                                                                                                                                 solved["FOV"],
                                                                                                                                 solved["Matches"]), title="Location", location=(1280,0), text_color="White")
    except:
        sg.popup_ok("No match has been found.", title="Your Location", location=(1280,0), text_color="White")
        
def main():
    '''
    This is the main function that controls the entire program. It has all been wrapped inside a function for easy exit of the various options using a function return

    It has no explicit inputs or returns. Its main purpose is to allow the while loop to run and for pysimplegui to keep the window open whilst showing a live feed of what the camera is seeing.
    
    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    # create instance and load default_database (built with max_fov=12 and the rest as default)
    t3 = Tetra3('default_database')
    
    # create the GUI window using create_window() which takes the layout function as its argument
    window = create_window(create_layout(Parameters()))

    # set the default option for whether or not to convert the .jpg image to .dng
    DNG_convert = False
    
    # set the default save folder for the images
    cam_folder_save = Parameters.default_save_folder
    
    # if images folder does not exist, create it
    if not os.path.isdir(cam_folder_save):
        os.mkdir(cam_folder_save)
        
    # set the default save folder for the videos
    vid_folder_save = Parameters.default_save_folder_vid
    
    # if videos folder does not exist, create it
    if not os.path.isdir(vid_folder_save):
        os.mkdir(vid_folder_save)
        
    # list of resolutions to view the live preview
    resolution_list = ["640 x 480", "1280 x 720", "1920 x 1080", "2560 x 1440"]
    
    # extract out the width and height from the resolution individually
    width, height = [int(num) for num in (resolution_list[0]).split() if num.isdigit()]
    
    # start the preview
    with picamera.PiCamera(resolution=(3280,2464)) as camera:
        camera.start_preview(resolution=(1440,1080), fullscreen=False, window=(0,0,640,480))
        time.sleep(1)
        
        # set a counter to be able to iterate through the resolution options
        res_counter = 0
        while True:
            # datetime object containing current date and time for time stamping the images and videos
            now = datetime.now()
        
            # dd/mm/YY H_M_S
            # note colons were removed as the RPi file system disliked moving files with colons in their name
            current_day_time = now.strftime("%d_%m_%Y_%H_%M_%S")
                
            # setup the events and values which the GUI will call and modify
            window, event, values = sg.read_all_windows(timeout=0)
            
            # set the date-time if specified
            if event == 'Set Date-Time':
                set_date_time()
            
            # run the plate solver
            if event == 'Where am I?':
                plate_solver(t3, Parameters.default_last_image)
                #plate_solver(t3, "tetra3/test_data/2019-07-29T204726_Alt60_Azi45_Try1.tiff")
                
            # run the image stacking capability
            if event == 'Stacking Wizard':
                images = image_stacking()
                
            # change the default save location if selected from the Menu
            if event == 'Save Location':      
                cam_folder_save = sg.PopupGetFolder('save_folder', initial_folder='{}'.format(Parameters.default_save_folder), no_window=True, keep_on_top=True)            

            # if the user selects the last image option
            if event == 'Last Image': 
                create_image_window(Parameters.default_last_image)
                
            if values['convertdng'] is True:
                DNG_convert = True

            # declare the camera settings if they ahve been changed
            cam_brightness  = int(values['brightness_slider'])    # Grabs the user set brightness value
            cam_contrast    = int(values['contrast_slider'])      # Grabs the user set contrast value
            cam_saturation  = int(values['saturation_slider'])    # Grabs the user set saturation value
            cam_sharpness   = int(values['sharpness_slider'])     # Grabs the user set sharpness value
            cam_exposure    = int(values['exposure_slider'])      # Grabs the user set exposure value
            cam_no_images   = int(values['no_images_slider'])     # Grabs the user set number of images to be taken
            cam_time_step   = int(values['time_step_slider'])     # Grabs the user set time increment between images
            cam_vid_time    = values['video_duration_slider']     # Grabs the user set video length
        
            # change the camera settings for the preview
            camera.brightness = cam_brightness  # brightness     min: 0   , max: 255 , increment:1 
            camera.contrast   = cam_contrast    # contrast       min: 0   , max: 255 , increment:1  
            camera.saturation = cam_saturation  # saturation     min: 0   , max: 255 , increment:1
            camera.sharpness  = cam_sharpness   # sharpness      min: 0   , max: 255 , increment:1
                    
            # closing the program by pressing exit
            if event == sg.WIN_CLOSED or event == 'Exit':
                # stop the live preview
                camera.stop_preview()
                # close the camera
                camera.close()
                # close the GUI window
                window.close()
                
                return
            
            # increase in live preview size
            if event == "+ Resize +":
                # iterate up the resolution options
                if res_counter == len(resolution_list) - 1:
                    pass
                else:
                    res_counter += 1
                
                width, height = [int(num) for num in (resolution_list[res_counter]).split() if num.isdigit()]

                # restart the preview with the new specified resolution
                camera.start_preview(resolution=(width,height), fullscreen=False, window=(0,0,width,height))
                # add a short pause to allow the preview to load correctly
                time.sleep(1)
            
            # decrease in live preview size
            if event == "- Resize -":
                # iterate down the resolution options
                if res_counter == 0:
                    pass
                else:
                    res_counter -= 1
                
                width, height = [int(num) for num in (resolution_list[res_counter]).split() if num.isdigit()]
                
                # restart the preview with the new specified resolution
                camera.start_preview(resolution=(width,height), fullscreen=False, window=(0,0,width,height))
                # add a short pause to allow the preview to load correctly
                time.sleep(1)
            
            if event == "Crosshair On":
                img = Image.open(os.path.join(os.path.dirname(sys.argv[0]),'crosshair.png')).convert('RGBA')
               
                preview_overlay(camera, (width,height), img)
            
            if event == "Crosshair Off":
                remove_overlays(camera)
                
            # record video
            if event == 'Record':
                # update the activity notification
                window.FindElement('output').Update('Working...')
                window.Refresh()

                # specify the name of the video save file
                video_save_file_name = "{}/Video_{}_{}s.yuv".format(vid_folder_save, current_day_time, cam_vid_time)
                
                # update the activity notification
                window['output'].update('Working...')
                 
                 # set the resolution for the video capture
                camera.resolution=(3296,2464)
                
                # start the video recording.
                # we use yuv format 
                camera.start_recording(video_save_file_name, format='yuv')
                camera.wait_recording(cam_vid_time)
                camera.stop_recording()
                    
                # reset the activity notification
                window.FindElement('output').Update('Idle')
                window.Refresh()
        
            # capture image
            elif event == 'Capture':
                # update the activity notification
                window.FindElement('output').Update('Working...')
                window.Refresh()
                
                # turn on the grey scale option if it is toggled
                if values['greyscale'] is True:
                    camera.color_effects = (128,128)
                else:
                    camera.color_effects = None
                
                # check if the dark, light, flat or bias options are selected
                # if they are then specify an append to the image filename
                file_append = ''
                if values['dark'] is True:
                    file_append = file_append + '_dark'
                if values['light'] is True:
                    file_append = file_append + '_light'
                if values['flat'] is True:
                    file_append = file_append + '_flat'
                if values['bias'] is True:
                    file_append = file_append + '_bias'
                
                # triggers long exposure
                if cam_exposure > 1:
                    # triggers multiple exposures
                    for i in range(cam_no_images):
                        # change the framerate of the camera
                        camera.framerate = 1/cam_exposure
                        
                        # convert the exposure time in seconds to microseconds
                        camera.shutter_speed = int(cam_exposure * 1E6)
                        
                        # set the camera ISO to 800
                        camera.iso = 800
                        
                        # give camera a long time to set gains and
                        # measure AWB (we may wish to use fixed AWB instead)
                        sleep(30)
                        camera.exposure_mode = 'off'
                        # automate the name of the file save name
                        image_save_file_name = '{}/Image_{}_no-{}_LE_{}s{}.jpeg'.format(cam_folder_save, current_day_time, i, cam_exposure, file_append)
                        # capture the image in RAW format
                        camera.capture(image_save_file_name, format='jpeg', bayer=True)
                        # if specified convert the jpeg image to a DNG image
                        if DNG_convert:
                            convert_to_DNG(image_save_file_name)
                            
                    # reset the framerate for the live preview
                    camera.framerate = 30
                    
                    # reset the camera exposure mode to auto
                    camera.exposure_mode = 'auto'
                # triggers multiple exposures
                else:
                    for i in range(cam_no_images):
                        # specify image file name
                        image_save_file_name = "{}/Image_{}_no-{}{}.jpeg".format(cam_folder_save, current_day_time, i, file_append)
                        
                        # capture the image in RAW format
                        camera.capture(image_save_file_name, format='jpeg', bayer=True)

                        # this creates the time gap between images being taken using the value set by the user
                        time.sleep(cam_time_step)

                        # if specified convert the jpeg image to a DNG image
                        if DNG_convert:
                            convert_to_DNG(image_save_file_name)

                        i += 1
                    i = 0

                # set the default last image to be shown. blackimage.png
                Parameters.default_last_image = image_save_file_name
                
                # reset the activity notification
                window.FindElement('output').Update('Idle')
                window.Refresh()

            # reset the camera settings to the default values
            elif event == 'Defaults':
                window.FindElement('brightness_slider').Update(Parameters.default_brightness)
                window.FindElement('contrast_slider').Update(Parameters.default_contrast)     
                window.FindElement('saturation_slider').Update(Parameters.default_saturation)    
                window.FindElement('sharpness_slider').Update(Parameters.default_sharpness)     
                window.FindElement('exposure_slider').Update(Parameters.default_exposure)   
                window.FindElement('no_images_slider').Update(Parameters.default_image_no)   
                window.FindElement('time_step_slider').Update(Parameters.default_time_step)   
                window.FindElement('video_duration_slider').Update(Parameters.default_vid_time)    

# run the main function
main()
