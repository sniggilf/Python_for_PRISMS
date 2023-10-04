multiproc   (10.2023)
------------------------------------------------------------
updates to code:
-includes two-way shift check between bands for alignment of each cube
-outputs all possible necessary file formats which can be changed by user 

1. Put your folder(s) of raw data in same directory as all codes (pWhite_multi.py, pTarget_multi.py, multiproc.py) and the 'files' folder containing CIE standards and other files necessary for the code to run.

2. Open windows command prompt and change to the directory containing the codes 
(cd .. -> goes down a directory)
(cd directoryname   -> goes up to the directory named e.g. 'directoryname')

3. To run the code use command:
> python multiproc foldername

4.After running the code, you should be able to select the .v image containing the white standard from within your folder 
and then select the ROI (white area) from this selected image (does not have to be named 'white').


output: foldername_PROC 
(See end of 'pTarget_multi.py' to change if necessary)
As default all of these folders of data are produced as output into the foldername_PROC directory:
>spectral_tiff
>RGB_tiff
>vips
>XYZ_tiff
>LAB_tiff
>RGB_pngs

(See end of 'pTarget_multi.py' to change outputs if necessary by commenting out selected lines from ln 384 onwards)
