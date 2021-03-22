Python_for_PRISMS
----------------------------------------------

The steps to get started are:


1. Download the libvips library for Windows and unzip to somewhere like c:\vips-x.y.z  (e.g. c:\vips-8.10.5 latest version)


Download it from here : 

https://github.com/libvips/libvips/releases/

e.g. for windows download of version 8.10.5:

https://github.com/libvips/libvips/releases/download/v8.10.5/vips-dev-w64-web-8.10.5.zip


2. Add c:\vips-x.y.z\bin\ to your PATH. (To do this go to 'edit the system environment variables' in Windows, 
and in advanced go to environment variables, and in system variables PATH, add this to the list.)

 

3. Download and install a 64-bit Python from https://www.python.org/downloads/ , run the downloaded installer and 
   choose customised installation. Here, check the box which allows you 
   to *add Python to environment variables* in installer options.

 

4. Install the binding with

 

    > pip install pyvips



(This is typed in command prompt, run as admin)



5. Whilst there you should also install any other missing modules:



    > pip install opencv-python    (for module cv2)

    > pip install matplotlib

    > pip install scipy



...and anything else that comes up as missing if trying to run code...

 

 6. python codes can then be run in command prompt using 'python XXXX.py' 
   where XXXX is the name of the python code.
