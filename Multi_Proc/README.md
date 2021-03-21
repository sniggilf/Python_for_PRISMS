multiproc 
------------------------------------------------------------

command:
> python multiproc foldername


Output: foldername_PROC folder containing all XXXX.final.v and XXXX.RGB16.v files and a file, foldername_3D.txt, 
file containing position info for each cube.

When running the code, you should be able to select the image containing the white standard from within your folder and then select 
the ROI (white area) from this selected image (does not have to be named 'white').

Note: Put your folder(s) in same directory as all codes (multiproc.py, pWhite_multi.py, pTarget_multi.py, read_positions.py) and the 'files' folder.
	  Flat Fielding and Dark corrections are ignored here. For flat & dark correction use single_proc per image.
	  

