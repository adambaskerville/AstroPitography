import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import PySimpleGUI as sg
from PIL import Image


def folder_file_selecter(gui_manager: Any) -> List[str]:
    """
    This function offers a popup menu allowing for multiple images to be selected

    It views a file and file tree

    Note, if scanning a large folder then tkinter will eventually complain about too many bitmaps.

    This can be fixed by reusing the images within PySimpleGUI (TODO: implement if needed at some point)

    Parameters:
        - gui_manager (Any): The GUI manager instance.

    Returns:
        - List[str]: List of selected image paths.
    """
    # base64 versions of images of a folder and a file. PNG files (may not work with PySimpleGUI27, swap with GIFs)
    folder_icon = b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII="
    file_icon = b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC"

    # create popup which lets user select folder with images
    starting_path = sg.popup_get_folder("Select Folder to display")

    if not starting_path:
        sys.exit(0)

    treedata = sg.TreeData()

    def add_files_in_folder(parent, dirname):
        """
        This builds the file tree by looping through the selected folder

        Parameters
        ----------
        parent  :

        dirname : str
                The directory where the images are located
        Returns
        -------
        None
        """
        files = os.listdir(dirname)
        for f in files:
            fullname = os.path.join(dirname, f)
            if os.path.isdir(fullname):  # if it's a folder, add folder and recurse
                treedata.Insert(parent, fullname, f, values=[], icon=folder_icon)
                add_files_in_folder(fullname, fullname)
            else:
                treedata.Insert(
                    parent,
                    fullname,
                    f,
                    values=[os.stat(fullname).st_size],
                    icon=file_icon,
                )

    add_files_in_folder("", starting_path)

    layout = [
        [sg.Text("Select images to stack")],
        [
            sg.Tree(
                data=treedata,
                headings=[
                    "Size",
                ],
                auto_size_columns=True,
                select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                num_rows=20,
                col0_width=40,
                key="-TREE-",
                show_expanded=False,
                enable_events=True,
            ),
        ],
        [sg.Button("Ok"), sg.Button("Cancel")],
    ]

    window = sg.Window("Image tree", layout, resizable=True, finalize=True)
    gui_manager.window = window
    gui_manager.window["-TREE-"].expand(
        True, True
    )  # resize with the window (Full support for Tree element being released in 4.44.0)

    while True:  # Event Loop
        event, images = gui_manager.window.read()
        if event in (sg.WIN_CLOSED, "Cancel", "Ok"):
            break

    gui_manager.window.close()
    return images["-TREE-"]


def set_date_time():
    """
    This function allows for the time and date to be set on the raspberry pi from within the GUI
    For headless RPi setups this is very useful as it cannot use NTP time synchronisation with no WiFi

    It simply takes user input for the date and time and runs a shell command using the os module: 'sudo date -s date_time'

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    # popup window to input date and time
    date_time = sg.popup_get_text(
        "Set Raspberry Pi Date and Time. Format: yyyy-mm-dd hh:mm:ss",
        "Input date and time",
        text_color="White",
    )

    # run the command
    os.system('sudo date -s "{}"'.format(date_time))


def plate_solver(star_database, img_path):
    """
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
    """
    print("Solving for image at: " + str(img_path))
    with Image.open(str(img_path)) as img:
        solved = star_database.solve_from_image(
            img
        )  # Adding e.g. fov_estimate=11.4, fov_max_error=.1 improves performance

    try:
        sg.popup_ok(
            "Right Ascension (RA) = {:.6f}\nDeclination (DEL) = {:.6f}\nRoll = {:.6f}\nField Of View = {:.3f}\nMatches = {}".format(
                solved["RA"],
                solved["Dec"],
                solved["Roll"],
                solved["FOV"],
                solved["Matches"],
            ),
            title="Location",
            location=(1280, 0),
            text_color="White",
        )
    except:
        sg.popup_ok(
            "No match has been found.",
            title="Your Location",
            location=(1280, 0),
            text_color="White",
        )


def image_stacking(gui_manager):
    """
    This function controls image stacking (averaging)
    It opens up a seperate window where images can be selected
    It then

    Parameters
    ----------

    Returns
    -------

    """
    # open up
    images = folder_file_selecter(gui_manager)

    return images
