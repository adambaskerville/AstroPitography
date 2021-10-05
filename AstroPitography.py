#! /usr/bin/python3 
'''
    Name    : AstroPitography
    Author  : Dr Adam Luke Baskerville
    Date    : 26-Sep-2021
    Version : 1-03
    
    Description
    -----------
    This program provides a simple user interface to control the raspberry pi HQ camera for use in astrophotography. It makes use of opencv, raspistill and PySimpleGUI
    
    A variety of camera settings can be controlled including:
    
    * Brightness
    * Contrast
    * Saturation
    * Sharpness
    * Exposure (shutter speed in this instance)
    * Time delay between images
    
    It is currently able to do the following:
    
    * Show a live preview of the camera view in the main window; useful for making sure something is in frame
    * Allows for capturing of single images, multiple images with time delay and long exposure imaging
    * When a picture is taken it will be visible next to the live video feed and if it is a poor image it can be deleted from within the program
    * The default save location can also be selected from within the window; handy for saving to USB stick etc... especially for large RAW files
    * Video capturing340
    * The image format is RAW, preferred over .png so no information is lost/processed
    
    More features will be added over time including:
    
    * Allow for greater variability in shutter speed (should be simple to implement)
    * Improve framerate of live preview [done]
    * Test! (when the skies improve!)
    * Improve video implementation
    * Image stacking capability
    * The ability to load camera presets for different objects (e.g. planetary, deep sky etc...)
    * Implement PySimpleGUIWeb for easier access on multiple devices. This has been worked on but there are significant lag issues and issues with write permissions when saving and loading the images 

    If you want the program to start on startup add this to the bottom of .bashrc:
    
'''
import os
import time
import PySimpleGUI as sg
import cv2
import imutils
import numpy as np
import PIL.Image
import io
import base64
import subprocess
from pidng.core import RPICAM2DNG
from datetime import datetime
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

# default font size for text elements
GUI_TEXT_SIZE = (int(SCREEN_WIDTH/60), 1)

# default size for spin box elements
SPIN_SIZE = (int(SCREEN_WIDTH/35), int(SCREEN_WIDTH/35))

# put all key parameters in their own class, Parameters
class Parameters:
    default_brightness   = 50
    default_contrast     = 0 
    default_saturation   = 0
    default_sharpness    = 0
    default_image_no     = 1
    default_exposure     = 1
    default_time_step    = 2
    default_vid_time     = 10
    default_image_size   = (int(SCREEN_HEIGHT/2), int(SCREEN_HEIGHT/2))
    default_preview_size = int(SCREEN_HEIGHT/2) 
    default_save_folder  = "{}/images".format(os.getcwd())
    scaling = None
    DNG_convert = False

def convert_to_bytes(file_or_bytes, resize=None):
    '''
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object
    
    Turns into  PNG format in the process so that can be displayed by tkinter/PySimpleGUI
    
    Parameters
    ----------
    file_or_bytes : Union[str, bytes]
                    Either a string filename or a bytes base64 image object

    resize        : Tuple[int, int] or None
                    optional new size

    Returns
    -------
    bio           : bytes
                    a byte-string object

    '''
    if isinstance(file_or_bytes, str):
        img = PIL.Image.open(file_or_bytes)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = PIL.Image.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.ANTIALIAS)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img

    return bio.getvalue()

def call_raspistill(command, cap):
    '''
    Will send a command to raspistill using the shell via. a subprocess. It controls releasing of the camera from opencv and restarts after the subprocess has ended
    
    Makes use of the greater camera control offered by raspistill (allows for RAW capture which opencv does not)
    
    Parameters
    ----------
    command: str
             string filename 

    cap    : None 
             the capture constructor from opencv

    Returns
    -------
    cap    : <class 'cv2.VideoCapture'>
             the capture constructor
    '''
    # call the raspistill subprocess
    # -r = raw capture
    # -t = timeout in milliseconds
    # -md = mode. mode=3 corresponds to 4056 x 3040 with 4:3 aspect ration. Frame rate = 0.005 - 10fps. Full FOV and no binning/scaling done
    
    # release the camera from opencv so raspistill can use it
    cap.release()
    # run the subprocess
    subprocess.call(command, shell=True)
    # restart the camera
    cap = cv2.VideoCapture(-1)
    # restart the recording
    recording = True
    
    return cap

def convert_to_DNG(image_save_file_name):
    '''
    This function will crate a DNG image from the .jpg + .raw data using PiDNG

    Parameters
    ----------
    file_or_bytes : str
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
    menu_def = [['Menu', ['Save Location', 'Exit']],
               ]     

    # define the column layout for the GUI
    image_column = [
        [sg.Image(filename='', key='video')],
        [sg.Image(filename='', key='image')],
        [sg.Button('Delete', size=(10, 1), font='Helvetica 14')],
    ]

    controls_column1 = [
        [sg.Text('Grey scale:', font=("Helvetica", 10), size=GUI_TEXT_SIZE),
        sg.Checkbox('', size=GUI_TEXT_SIZE, enable_events=True, key='greyscale')],
        [sg.Text('White balance:', font=("Helvetica", 10), size=GUI_TEXT_SIZE),
        sg.Checkbox('', size=GUI_TEXT_SIZE, enable_events=True, key='whitebalance')],
        [sg.Text('Convert to DNG:', font=("Helvetica", 10), size=GUI_TEXT_SIZE),
        sg.Checkbox('', size=GUI_TEXT_SIZE, enable_events=True, key='convertdng')],
        [sg.Text('Brightness', font=("Helvetica", 10), size=GUI_TEXT_SIZE),                
        sg.Spin([i for i in range(0, 100)], initial_value=p.default_brightness, font=('Helvetica', 20), key='brightness_slider')],
        [sg.Text('Contrast', font=("Helvetica", 10), size=GUI_TEXT_SIZE),      
        sg.Spin([i for i in range(-100, 100)], initial_value=p.default_contrast, font=('Helvetica', 20), key='contrast_slider')],
        [sg.Text('Saturation', font=("Helvetica", 10), size=GUI_TEXT_SIZE),               
        sg.Spin([i for i in range(-100, 100)], initial_value=p.default_saturation, font=('Helvetica', 20), key='saturation_slider')],
        [sg.Text('Sharpness', font=("Helvetica", 10), size=GUI_TEXT_SIZE),               
        sg.Spin([i for i in range(0, 100)], initial_value=p.default_sharpness, font=('Helvetica', 20), key='sharpness_slider')], 
    ]

    controls_column2 = [
        [sg.Text('', font=("Helvetica", 10), size=GUI_TEXT_SIZE)],
        [sg.Text('', font=("Helvetica", 10), size=GUI_TEXT_SIZE)],
        [sg.Text('Exposure / s', font=("Helvetica", 10), size=GUI_TEXT_SIZE),               
        sg.Spin([i for i in range(0, 200)], initial_value=p.default_exposure, font=('Helvetica', 20), key='exposure_slider')],
        [sg.Text('Number of images', font=("Helvetica", 10), size=GUI_TEXT_SIZE),               
        sg.Spin([i for i in range(1, 100)], initial_value=p.default_image_no, font=('Helvetica', 20), key='no_images_slider')],
        [sg.Text('Time step / s', font=("Helvetica", 10), size=GUI_TEXT_SIZE),               
        sg.Spin([i for i in range(0, 100)], initial_value=p.default_time_step, font=('Helvetica', 20), key='time_step_slider')],
        [sg.Text('Video duration / s', font=("Helvetica", 10), size=GUI_TEXT_SIZE),               
        sg.Spin([i for i in range(1, 100)], initial_value=p.default_vid_time, font=('Helvetica', 20), key='video_duration_slider')], 
    ]

    controls_column3 = [
        [sg.Button('Capture', size=(10, 1), font='Helvetica 14'),
         sg.Button('Record', size=(10, 1), font='Helvetica 14'),
         sg.Button('Defaults', size=(10, 1), font='Helvetica 14'),
         sg.Button('Exit', size=(10, 1), font='Helvetica 14'),
         sg.Text('Status:', size=(6,1), font=('Helvetica', 18)),
         sg.Text('Idle', size=(8, 1), font=('Helvetica', 18), text_color='Red', key='output')]
    ]

    # define the window layout
    layout = [[sg.Menu(menu_def, )],
              [sg.Column(image_column),
               sg.Frame("Controls", layout=[[sg.Column(controls_column1), 
                                             sg.VerticalSeparator(),
                                             sg.Column(controls_column2)],
                                             [sg.Column(controls_column3)]]),
              ],   
              #[sg.InputText('{}'.format(p.default_save_folder), key='save_folder'), sg.FolderBrowse()],   
              ]
                     
    return layout

def create_window(layout):
    '''
    This is the function that builds the GUI window using a supplied layout

    Parameters
    ----------
    layout : List[List[Element]]
             A list containing all the obejcts that are to be displayed in the GUI

    Returns
    -------
    window : Window object
             The GUI window with al lspecified elements displayed
    '''
    # create invisible window with no layout
    window = sg.Window('AstroPitography', [[]], location=(0,0), 
                                                keep_on_top=False, 
                                                finalize=True, 
                                                resizable=False, 
                                                no_titlebar=False, # set this to False so popups sit on top of the main window
                                                auto_size_buttons=True, 
                                                grab_anywhere=False,
                                                size=(SCREEN_WIDTH,SCREEN_HEIGHT))

    # apply scaling using tkinter to scale the GUI elements, then add the layout
    window.TKroot.tk.call('tk', 'scaling', 2.2)
    window.extend_layout(window, layout)
    #window.refresh()

    # this loads a placeholder black image before an image is taken. TODO: Implement a better way to do this
    placeholder_img = "blackimage.png"
    
    window['image'].update(data=convert_to_bytes(placeholder_img, resize=Parameters.default_image_size))

    return window

def main():
    '''
    This is the main function that controls the entire program. It has all been wrapped inside a function for easy exit of the various options using a function return

    It has no explicit inputs or returns. Its main purpose is to allow the while loop to run and for pysimplegui to keep the window open whilst showing a live feed of what the camera is seeing.
    
    '''
    # create the GUI window using create_window() which takes the layout function as its argument
    window = create_window(create_layout(Parameters()))

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #
    cap = cv2.VideoCapture(-1) # cap = cv2.VideoCapture(-1) for raspberry pi HQ camera

    # start the preview as soon as the window opens
    recording = True
    
    # set the default option for whether or not to convert the .jpg image to .dng
    DNG_convert = False
    
    # set the default save folder for the images
    cam_folder_save = Parameters.default_save_folder

    while True:
        # datetime object containing current date and time for time stamping the images and videos
        now = datetime.now()
        
        # dd/mm/YY H_M_S
        # note colons were removed as the RPi file system disliked moving files with colons in their name
        current_day_time = now.strftime("%d_%m_%Y_%H_%M_%S")
        
        # setup the events and values which the GUi will call and modify
        event, values = window.read(timeout=0)
        
        # change the default save location if selected from the Menu
        if event == 'Save Location':      
           cam_folder_save = sg.PopupGetFolder('save_folder', initial_folder='{}'.format(Parameters.default_save_folder), no_window=True, keep_on_top=True)            

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
        cap.set(10, cam_brightness ) # brightness     min: 0   , max: 255 , increment:1 
        cap.set(11, cam_contrast   ) # contrast       min: 0   , max: 255 , increment:1  
        cap.set(12, cam_saturation ) # saturation     min: 0   , max: 255 , increment:1
        cap.set(10, cam_brightness ) # brightness     min: 0   , max: 255 , increment:1
        
        # convert from micro seconds to seconds. Maximum shutter delay for HQ camera appears to be 200 seconds (test this)
        cam_exposure_convert = cam_exposure*1E6
        
        # closing the program by pressing exit
        if event == sg.WIN_CLOSED or event == 'Exit':
            cap.release()
            return
            
        # record video
        elif event == 'Record':
            # update the activity notification
            window.FindElement('output').Update('Working...')
            window.Refresh()

            # specify the name of the video save file
            video_save_file_name = "{}/Video_{}_{}s.avi".format(cam_folder_save, current_day_time, cam_vid_time)
            width        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            size         = (width, height)
            fourcc       = cv2.VideoWriter_fourcc(*'XVID')
            video_writer = cv2.VideoWriter(video_save_file_name, fourcc, 20.0, size)
            
            # record video of specified length
            start_time = time.time()
            while ( int(time.time() - start_time) < cam_vid_time ):
                ret, frame = cap.read()

                if ret == True:
                    # update the activity notification
                    window['output'].update('Working...')
                    
                    frame = cv2.flip(frame,0)
                    video_writer.write(frame)

            video_writer.release()

            # reset the activity notification
            window.FindElement('output').Update('Idle')
            window.Refresh()
        # record image
        elif event == 'Capture':
            # update the activity notification
            window.FindElement('output').Update('Working...')
            window.Refresh()

            # triggers long exposure
            if cam_exposure > 1:
                # triggers multiple exposures
                for i in range(cam_no_images):
                    image_save_file_name = "{}/Image_{}_no-{}_LE_{}s.jpg".format(cam_folder_save, current_day_time, i, cam_exposure)

                    # setup the raspistill command
                    long_exposure = 'raspistill --nopreview -r -t 10 -md 3 -ex off -ag 1 --shutter {} -ISO 800 -st -o {}'.format(cam_exposure_convert, image_save_file_name)
                    
                    if values['greyscale'] is True:
                        greyscale_option = ' -cfx 128:128' # settings for greyscale image
                        long_exposure = long_exposure + greyscale_option # add option to raspistill command string
                        
                    if values['whitebalance'] is True:
                        whitebalance_option = " -awb off -awbg '1.0,1.0'"
                        long_exposure = long_exposure + whitebalance_option
                        
                    # call out using subprocess
                    cap = call_raspistill(long_exposure, cap)

                    # update the still image with the most recent image taken. The image is resized to fit better into the GUI                   
                    window['image'].update(data=convert_to_bytes(image_save_file_name, resize=Parameters.default_image_size))

                    if DNG_convert:
                        convert_to_DNG(image_save_file_name)
                        
                                   
            # triggers multiple exposures
            else:
                for i in range(cam_no_images):
                    # specify image file name
                    image_save_file_name = "{}/Image_{}_no-{}.jpg".format(cam_folder_save, current_day_time, i)
                    # setup the raspistill command
                    raw_capture = 'raspistill -r -md 3 --nopreview --brightness {} --contrast {} --saturation {} --sharpness {} -ISO 800 -st -o {}'.format(cam_brightness,
                                                                                                                                                           cam_contrast,
                                                                                                                                                           cam_saturation,
                                                                                                                                                           cam_sharpness,
                                                                                                                                                           image_save_file_name)
                    if values['greyscale'] is True:
                        greyscale_option = ' -cfx 128:128' # settings for greyscale image
                        raw_capture = raw_capture + greyscale_option # add option to raspistill command string
                        
                    if values['whitebalance'] is True:
                        whitebalance_option = " -awb off -awbg '1.0,1.0'"
                        raw_capture = raw_capture + whitebalance_option
                        
                    # call out using subprocess
                    cap = call_raspistill(raw_capture, cap)

                    # this creates the time gap between images being taken using the value set by the user
                    time.sleep(cam_time_step)
                    
                    # update the still image with the most recent image taken. The image is resized to fit better into the GUI.
                    window['image'].update(data=convert_to_bytes(image_save_file_name, resize=Parameters.default_image_size))

                    if DNG_convert:
                        convert_to_DNG(image_save_file_name)

                    i += 1
                i = 0

            # reset the activity notification
            window.FindElement('output').Update('Idle')
            window.Refresh()

        # if image is not good, pressing the delete button will remove it
        elif event == 'Delete':
            try:
                os.remove(image_save_file_name)
                placeholder_img = "blackimage.png"
                window['image'].update(data=convert_to_bytes(placeholder_img, resize=Parameters.default_image_size))
            except:
                print("File not found, continuing.")
                pass

        # reset the camera settings to the default values. TODO: Add these to a dictionary at some point for easier access
        elif event == 'Defaults':
            window.FindElement('brightness_slider').Update(Parameters.default_brightness)
            window.FindElement('contrast_slider').Update(Parameters.default_contrast)     
            window.FindElement('saturation_slider').Update(Parameters.default_saturation)    
            window.FindElement('sharpness_slider').Update(Parameters.default_sharpness)     
            window.FindElement('exposure_slider').Update(Parameters.default_exposure)   
            window.FindElement('no_images_slider').Update(Parameters.default_image_no)   
            window.FindElement('time_step_slider').Update(Parameters.default_time_step)   
            window.FindElement('video_duration_slider').Update(Parameters.default_vid_time)    

        if recording:
            ret, frame = cap.read()
            frame = imutils.resize(frame, width=Parameters.default_preview_size)
            imgbytes = cv2.imencode('.ppm', frame)[1].tobytes()
            # NOTE: Changed from .png to .ppm. A PhotoImage which per its docstring "can display images in PGM, PPM, GIF, PNG format"
            # GIF is lossy, PGM is grayscale, and PNG is slow to encode
            # PPM is a naive format which is large but fast to process 
            # Since processing is the bottleneck here and not memory capacity/bandwidth, this is a lot faster
            window['video'].update(data=imgbytes)

# Run the main function
main()
cv2.destroyAllWindows()