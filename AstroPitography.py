'''
    Name    : AstroPitography
    Author  : Dr Adam Luke Baskerville
    Date    : 05-Nov-2020
    Version : 1-06
    
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
    * Video capturing
    * The image format is RAW, preffered over .png so no information is lost/processed
    
    This is still new (v1-05) and has not had much testing. More features will be added over time including:
    
    * Allow for greater variability in shutter speed (should be simple to implement)
    * Improve framerate of live preview
    * Test! (when the skies improve!)
    * Improve video implementation
    * Image stacking capability
    * The ability to load camera presets for different objects (e.g. planetary, deep sky etc...)
    * Implement PySimpleGUIWeb for easier access on multiple devices. This has been worked on but there are significant lag issues and issues with write permissions when saving and loading the images 

    If you want the program to start on startup add this to the bottom of .bashrc:
    
    
    python3
'''

import os
import time
from os.path import expanduser
import PySimpleGUI as sg
import cv2
import imutils
import numpy as np
import PIL.Image
import io
import base64
import subprocess
from pydng.core import RPICAM2DNG
from datetime import datetime
#import PySimpleGUIWeb as sg

# set the GUI theme
sg.theme('DarkBlack')

def convert_to_bytes(file_or_bytes, resize=None):
    '''
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object
    
    Turns into  PNG format in the process so that can be displayed by tkinter/PySimpleGUI
    
    :param file_or_bytes: either a string filename or a bytes base64 image object
    :type file_or_bytes:  (Union[str, bytes])
    :param resize:  optional new size
    :type resize: (Tuple[int, int] or None)
    :return: (bytes) a byte-string object
    :rtype: (bytes)
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
    Will send a command to raspistill using the shell via. a subprocess. In controls releasing of the camera from opencv and restarts after the subprocess has ended
    
    Makes use of the greater camera control offered by raspistill (allows for RAW capture which opencv does not)
    
    :param command: string filename 
    :type file_or_bytes:  (str)
    :param cap:  the capture constructor from opencv
    :type resize: None
    :return: (cap) the capture constructor
    :rtype: (<class 'cv2.VideoCapture'>)
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

def main():
    '''
    This is the main function that controls the entire program. It has all been wrapped inside a function for easy exit of the various options using a function return
    It has no explicit inputs or returns. Its main purpose is to allow the while loop to run and for pysimplegui to keep the window open whilst showing a live feed of what the camera is seeing.
    
    '''
    # Default camera values
    default_brightness   = 50
    default_contrast     = 0 
    default_saturation   = 0
    default_sharpness    = 0
    default_image_no     = 1
    default_iso          = 800
    default_exposure     = 1
    default_time_step    = 2
    default_vid_time     = 10
    default_image_size   = (340,340)
    default_preview_size = 340 
    default_save_folder  = "{}/PiAstroCam".format(expanduser("~"))

    # define the column layout b the GUI
    image_column = [ 
        [sg.Image(filename='', key='image'),
        sg.Button('Delete', size=(10, 1), font='Helvetica 14')],
    ]

    controls_column1 = [
        [sg.Text('Brightness', font=("Helvetica", 10), size=(20, 1)),               
        sg.Slider(range=(0, 100), orientation='h', size=(20, 20), default_value=default_brightness, key='brightness_slider')], 
        [sg.Text('Contrast', font=("Helvetica", 10), size=(20, 1)),      
        sg.Slider(range=(-100, 100), orientation='h', size=(20, 20), default_value=default_contrast, key='contrast_slider')],
        [sg.Text('Saturation', font=("Helvetica", 10), size=(20, 1)),               
        sg.Slider(range=(-100, 100), orientation='h', size=(20, 20), default_value=default_saturation, key='saturation_slider')], 
        [sg.Text('Sharpness', font=("Helvetica", 10), size=(20, 1)),               
        sg.Slider(range=(-100, 100), orientation='h', size=(20, 20), default_value=default_sharpness, key='sharpness_slider')], 
    ]

    controls_column2 = [
        [sg.Text('ISO', font=("Helvetica", 10), size=(20, 1)),               
        sg.Slider(range=(100, 800), orientation='h', size=(20, 20), default_value=default_iso, key='iso_slider')],
        [sg.Text('Exposure', font=("Helvetica", 10), size=(20, 1)),               
        sg.Slider(range=(0, 200), orientation='h', size=(20, 20), default_value=default_exposure, key='exposure_slider')], 
        [sg.Text('Number of images', font=("Helvetica", 10), size=(20, 1)),               
        sg.Slider(range=(0, 100), orientation='h', size=(20, 20), default_value=default_image_no, key='no_images_slider')], 
        [sg.Text('Time step', font=("Helvetica", 10), size=(20, 1)),               
        sg.Slider(range=(0, 100), orientation='h', size=(20, 20), default_value=default_time_step, key='time_step_slider')],
        [sg.Text('Video duration', font=("Helvetica", 10), size=(20, 1)),               
        sg.Slider(range=(1, 100), orientation='h', size=(20, 20), default_value=default_vid_time, key='video_duration_slider')], 
    ]

    extra_controls_column1 = [
        [sg.Text('Grey scale:', font=("Helvetica", 10), size=(10, 1)),
        sg.Checkbox('', size=(5,1), enable_events=True, key='greyscale'),
        sg.Text('Auto white balance off:', font=("Helvetica", 10), size=(20, 1)),
        sg.Checkbox('', size=(5,1), enable_events=True, key='whitebalance')],
        [sg.Text('h flip:', font=("Helvetica", 10), size=(10, 1)),
        sg.Checkbox('', size=(5,1), enable_events=True, key='hflip'),
        sg.Text('v flip:', font=("Helvetica", 10), size=(20, 1)),
        sg.Checkbox('', size=(5,1), enable_events=True, key='vflip')],
    ]
    
    # define the window layout
    layout = [[sg.Text('      Live Preview', size=(20, 1), justification='center', font='Helvetica 20'),
               sg.Text(' Most Recent Image', size=(30, 1), justification='center', font='Helvetica 20')],
              [sg.Image(filename='', key='video'),
                sg.Column(image_column)],
              [sg.Frame("Controls", layout=[[sg.Column(controls_column1), sg.Column(controls_column2)]])],
              [sg.Frame("Extra Controls", layout=[[sg.Column(extra_controls_column1)]])],
              [sg.Text('Choose A Directory to Save Images and Videos', size=(50, 1))],      
              [sg.Text('Your Folder', size=(15, 1), auto_size_text=False, justification='right'),      
               sg.InputText('{}'.format(default_save_folder), key='save_folder'), sg.FolderBrowse()],      
              [sg.Button('Capture', size=(10, 1), font='Helvetica 14'),
               sg.Button('Record', size=(10, 1), font='Helvetica 14'),
               sg.Button('Defaults', size=(10, 1), font='Helvetica 14'),
               sg.Button('Exit', size=(10, 1), font='Helvetica 14'),
               sg.Text('Status:', size=(6,1), font=('Helvetica', 18)),
               sg.Text('Idle', size=(8, 1), font=('Helvetica', 18), text_color='Red', key='output')]]
 
    # create the window
    window = sg.Window('AstroPitography', layout, location=(0,0), keep_on_top=False).Finalize()
    #window.Maximize()

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #
    cap = cv2.VideoCapture(-1) # cap = cv2.VideoCapture(0) for laptop webcam
                               # cap = cv2.VideoCapture(-1) for raspberry pi HQ camera

    # start the preview as soon as the window opens
    recording = True
    # this loads a placeholder black image before an image is taken. TODO: Implement a better way to do this
    placeholder_img = "/home/pi/PiAstroCam/blackimage.png"
    #prev = 'raspistill --focus -t 0 -k'
    #cap = call_raspistill(prev, cap)
    
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=default_preview_size)
    window['image'].update(data=convert_to_bytes(placeholder_img, resize=default_image_size))
    
    while True:
        # datetime object containing current date and time for time stamping the images and videos
        now = datetime.now()
        # dd/mm/YY H:M:S
        current_day_time = now.strftime("%d:%m:%Y_%H:%M:%S")
        
        event, values = window.read(timeout=2)
        
        cam_brightness  = int(values['brightness_slider'])    # Grabs the user set brightness value
        cam_contrast    = int(values['contrast_slider'])      # Grabs the user set contrast value
        cam_saturation  = int(values['saturation_slider'])    # Grabs the user set saturation value
        cam_sharpness   = int(values['sharpness_slider'])     # Grabs the user set sharpness value
        cam_exposure    = int(values['exposure_slider'])      # Grabs the user set exposure value
        cam_iso         = int(values['iso_slider'])           # Grabs the user set ISO value
        cam_no_images   = int(values['no_images_slider'])     # Grabs the user set number of images to be taken
        cam_time_step   = int(values['time_step_slider'])     # Grabs the user set time increment between images
        cam_vid_time    = values['video_duration_slider']     # Grabs the user set video length
        cam_folder_save = values['save_folder']               # Grabs the user set save 

        # change the camera settings for the preview
        cap.set(10, cam_brightness ) # brightness     min: 0   , max: 255 , increment:1 
        cap.set(11, cam_contrast   ) # contrast       min: 0   , max: 255 , increment:1  
        cap.set(12, cam_saturation ) # saturation     min: 0   , max: 255 , increment:1
        cap.set(10, cam_brightness ) # brightness     min: 0   , max: 255 , increment:1
        
        # convert from micro seconds to seconds. Maximum shutter delay for HQ camera appears to be 200 seconds (test this)
        cam_exposure_convert = cam_exposure*1E6
        
        if event == 'Exit' or event == sg.WIN_CLOSED:
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
                    image_save_file_name = "{}/Image_{}_no:{}_LE_{}s.jpg".format(cam_folder_save, current_day_time, i, cam_exposure)
                    # setup the raspistill command
                    long_exposure = 'raspistill --nopreview -r -t 10 -md 3 -ex off -ag 1 --shutter {} -ISO {} -st -o {}'.format(cam_exposure_convert, cam_iso, image_save_file_name)
                    
                    if values['hflip'] is True:
                        hflip_option = ' --hflip' # setting for hflip
                        long_exposure = long_exposure + hflip_option # add option to raspistill command string
                        
                    if values['vflip'] is True:
                        vflip_option = ' --vflip' # setting for vflip
                        long_exposure = long_exposure + vflip_option # add option to raspistill command string
                        
                    if values['greyscale'] is True:
                        greyscale_option = ' -cfx 128:128' # settings for greyscale image
                        long_exposure = long_exposure + greyscale_option # add option to raspistill command string
                        
                    if values['whitebalance'] is True:
                        whitebalance_option = " -awb off -awbg '1.0,1.0'"
                        long_exposure = long_exposure + whitebalance_option
                        
                    # call out using subprocess
                    cap = call_raspistill(long_exposure, cap)
                    # update the still image with the most recent image taken. The image is resized to fit better into the GUI                   
                    window['image'].update(data=convert_to_bytes(image_save_file_name, resize=default_image_size))
                           
            # triggers multiple exposures
            else:
                for i in range(cam_no_images):
                    # specify image file name
                    image_save_file_name = "{}/Image_{}_no:{}.jpg".format(cam_folder_save, current_day_time, i)
                    # setup the raspistill command
                    raw_capture = 'raspistill --nopreview -t 10 -r -md 3 --brightness {} --contrast {} --saturation {} --sharpness {} -ISO {} -st -o {}'.format(cam_brightness,
                                                                                                                                                       cam_contrast,
                                                                                                                                                       cam_saturation,
                                                                                                                                                       cam_sharpness,
                                                                                                                                                       cam_iso,
                                                                                                                                                       image_save_file_name)
                    if values['hflip'] is True:
                        hflip_option = ' --hflip' # setting for hflip
                        raw_capture = raw_capture + hflip_option # add option to raspistill command string
                        
                    if values['vflip'] is True:
                        vflip_option = ' --vflip' # setting for vflip
                        raw_capture = raw_capture + vflip_option # add option to raspistill command string
                        
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
                    window['image'].update(data=convert_to_bytes(image_save_file_name, resize=default_image_size))
                    i += 1
                i = 0
            
            # automatically convert the raw data contained in the jpg file into a dng file using pydng
            raw_dng_convert = RPICAM2DNG()
            image_dng_filename = raw_dng_convert.convert(image_save_file_name)
            
            # remove the original jpg image to save space
            os.remove(image_save_file_name)
            
            # reset the activity notification
            window.FindElement('output').Update('Idle')
            window.Refresh()
        # if image is not good, pressing the delete button will remove it
        elif event == 'Delete':
            try:
                os.remove(image_dng_filename)
                placeholder_img = "/home/pi/PiAstroCam/blackimage.png"
                window['image'].update(data=convert_to_bytes(placeholder_img, resize=default_image_size))
            except:
                print("File not found, continuing.")
                pass
        # reset the camera settings to the default values. TODO: Add these to a dictionary at some point for easier access
        elif event == 'Defaults':
            window.FindElement('brightness_slider').Update(default_brightness)
            window.FindElement('contrast_slider').Update(default_contrast)     
            window.FindElement('saturation_slider').Update(default_saturation)    
            window.FindElement('sharpness_slider').Update(default_sharpness)    
            window.FindElement('exposure_slider').Update(default_exposure)
            window.FindElement('iso_slider').Update(default_iso)
            window.FindElement('no_images_slider').Update(default_image_no)   
            window.FindElement('time_step_slider').Update(default_time_step)   
            window.FindElement('video_duration_slider').Update(default_vid_time)    

        if recording:
            #prev = 'raspistill --focus -p '0, 0, 300, 300' -t 0'
            #cap = call_raspistill(prev, cap)
            ret, frame = cap.read()
            frame = imutils.resize(frame, width=default_preview_size)
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()
            window['video'].update(data=imgbytes)

# Run the main function
main()
cv2.destroyAllWindows()