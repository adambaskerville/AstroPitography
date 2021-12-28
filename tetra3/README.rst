Welcome to tetra3!
==================

*tetra3 is a fast lost-in-space plate solver for star trackers written in Python.*

Use it to identify stars in images and get the corresponding direction (i.e. right ascension and
declination) in the sky which the camera points to. The only thing tetra3 needs to know is the
approximate field of view of your camera.

The software is available in the `tetra3 GitHub repository <https://github.com/esa/tetra3>`_.
General instructions are available at the
`tetra3 ReadTheDocs website <https://tetra3.readthedocs.io/en/latest/>`_. tetra3 is Free and Open
Source Software released by the European Space Agency under the Apache License 2.0. See NOTICE.txt
in the repository for full licensing details.

Performance will vary, but in general solutions will take 10 milliseconds (excluding time to extract
star positions from images) with 10 arcsecond (50 microradian) accuracy.

A camera with a field of view of at least 10 degrees and 512 by 512 pixels is a good starting point.
It is important that the distortion of the lens is low to preserve the true shape of the star
patterns. Your camera should be able to acquire stars down to magnitude 6.5 for best results (for
a narrow field of view camera this becomes very important as there are few bright stars).

A real-world set of images acquired with a FLIR Blackfly S BFS-U3-31S4M-C (Sony IMX265 sensor;
binned 2x2) camera and a Fujifilm HF35XA-5M 35mm f/1.9 lens are included as test data (11.4 degrees
field of view).

To effectively use tetra3 with your camera you may need to build a database optimised for your use
case. See the API documentation for details on this. A database built for the test data is included
as default_database.npz and may suit your needs if you have a similar camera setup.
