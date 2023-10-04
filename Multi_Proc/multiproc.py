#Prog to align channels within a single image cube
# input args:
#white_in targets_folder
#FOLDER MUST INCLUDE ONE WHITE FOR ALL TARGETS
#
#NOT CURRENTLY USING DARK FILES OR FLAT FIELD CALIBRATION FILES - CHANGE THIS
#> python multiproc.py folder

import random
import subprocess
import sys
import string
import math
import numpy as np
import ntpath
import os
import sys
import pyvips
import glob
#checks python version to import correct tkinter version
if sys.version_info >= (3, 0): 
	from tkinter import filedialog
	from tkinter import *
	from tkinter.filedialog import askopenfilename
if sys.version_info < (3, 0): 
	from Tkinter import *
	import Tkinter, Tkconstants, tkFileDialog
	from Tkinter.tkFileDialog import askopenfilename


#import pWhite_new
#import pTarget_new

from array import *
from ctypes import *
from subprocess import call, Popen, PIPE


root = Tk()
root.wm_withdraw()

#get working directory
dir = os.getcwd()

foldername = sys.argv[1]


print('Folder name : %s \n' % (foldername))
#withdraw() # we don't want a full GUI, so keep the root window from appearing
print('Select file containing White Standard...')

whitefile = askopenfilename(initialdir=dir+foldername) # show an "Open" dialog box and return the path to the selected file
print('White File selected:', whitefile)

filenames=[]

#filenames = [(os.path.basename(x) for x in glob.iglob(dir+'\\'+foldername+'\\*.v')]
for file in glob.iglob(dir+'\\'+foldername+'\\*.v'):
	print(file)
	f = file.split('\\')[-1]
	if f.lower() not in str(whitefile).lower(): 
		print(f)
		filenames.append(f)
	#if 'white' in f.lower(): white = f
white = str(whitefile).split('/')[-1]
#print('white :', white)
os.system("python pWhite_multi.py %s %s" % (white, foldername))

with open(dir+'\\'+foldername+'_PROC\\'+foldername+'_3D.txt','w') as wf:
	wf.write('{0}\t{1}\t\t{2}\t\t{3}\n'.format('Filename', 'Altitude', 'Azimuth', 'Focus Position'))
	wf.write('---------------------------------------------------------------------------------------------------------\n')
	


for file in filenames:
	print('-----Image cube: %s-----' % (file))
	os.system("python pTarget_multi.py %s %s %s" % (file, white, foldername))

#print(filenames)



