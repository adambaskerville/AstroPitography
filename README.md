<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/adambaskerville/AstroPitography">
    <img src="AstroPitographyLogoSmall.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">AstroPitography</h3>

  <p align="center">
    Astrophotography + raspberry pi HQ camera = AstroPitography
    <br />
    <a href="https://github.com/github_username/AstroPitography/issues">Request Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About AstroPitography](#about-the-project)
  * [Built With](#built-with)
  * [Uses](#uses)
* [Getting Started](#getting-started)
* [Roadmap](#roadmap)

<!-- ABOUT THE PROJECT -->
## About AstroPitography

![AstroPitography](https://raw.githubusercontent.com/adambaskerville/AstroPitography/main/AstroPitography_GUI.png)

Astrophotography is an expensive pastime, scopes, driven mounts, cameras, eyepieces, etc... I have always enjoyed squeezing as much performance out of more limited hardware to see what the end results can be; so when the **£50** Raspberry Pi High Quality camera was released I wanted to see how it handles astrophotography. It will certainly not beat a top of the line DSLR or a ZWO camera which are several orders of magnitude more expensive and refined, but I wanted to see what can be achieved. I wrote this simple Python program to act as a basic GUI for when I am out with my telescope. The Raspberry Pi 3B+ and HQ camera were mounted together and using a 1.25 inch to C adapter sits in the telescope eyepiece position. I set up the Raspberry Pi to act as a wireless access point and connect to its network via VNC on my phone to conveniently interface with the GUI. A small Raspberry Pi screen will also work great or just hooking it up to a regular monitor will do.

I had originally used stellarmate with kstars etc... but wanted a simpler way to interface with the HQ camera. This is only the first iteration of the program which currently has the following features:

* Control important settings of the camera:
  * Brightness
  * Contrast
  * Saturation
  * Sharpness
  * Exposure (shutter speed in this instance)
  * Time delay between images
* Show a live preview of the camera view in the main window; useful for making sure something is in frame.
* Allows for capturing of single images, multiple images with time delay and long exposure imaging.
* When a picture is taken it will be visible next to the live preview. If it is a poor image it can be deleted from within the program.
* The default save location can be selected from within the program window; handy for saving to USB stick etc... especially for large RAW files.
* Timed video capturing.
* The image format is RAW, preferred over .png which processes the image.

### Built With

* [PySimpleGUI](https://pysimplegui.readthedocs.io/en/latest/)
* [OpenCV](https://opencv.org/)
* [Raspistill](https://www.raspberrypi.org/documentation/usage/camera/raspicam/raspistill.md)

### Uses
* [Raspberry Pi 3B+](https://thepihut.com/products/raspberry-pi-3-model-b-plus)
* [Raspberry Pi HQ Camera](https://thepihut.com/products/raspberry-pi-high-quality-camera-module)

In theory any Raspberry Pi should work, along with the other various Raspberry Pi cameras.

<!-- GETTING STARTED -->
## Getting Started

It is a self contained Python program. Type:

`python3 AstroPitography.py`

into a terminal on your raspberry pi to run the program. Editing your `.bashrc` can allow for the program to begin on startup.

<!-- ROADMAP -->
## Roadmap

 * More testing (when the skies finally improve here in rainy UK!)
 * Allow for fractional variability in shutter speed (simple to implement)
 * Improve framerate of live preview.
 * Improve features of video implementation.
 * The ability to load camera presets for different objects (e.g. planetary, deep sky etc...)
 * Automatic image stacking capability.
 * Implement PySimpleGUIWeb for easier access on multiple devices. Work has started on this but there are significant lag issues with the preview, and issues with write permissions when saving and loading the images. 

<!-- CONTACT -->
## Contact

Adam Baskerville - [@AdamBask](https://twitter.com/AdamBask) - ab695@sussex.ac.uk

Project Link: [https://github.com/adambaskerville/AstroPitography](https://github.com/adambaskerville/AstroPitography)
