#Program for quick check of entire macbeth chart as taken using PRISMS.

#INPUT: filename.final.v     <- processed PRISMS vips image file
#!!DIRECTORY MUST CONTAIN BOTH filename.final.v AND filename.RGB16.v TO RUN!!

#OUTPUT: filename_patches.jpeg    <- showing points at which reflectance spectra were sampled
#IF MACBETH CHART IS ROTATED, SOME REGIONS MAY NOT BE SELECTED PROPERLY, CAN CHECK IN OUTPUT IMAGE.

#IF WISH TO SAVE SPECTRAL PLOTS, CLICK ON SAVE BUTTON IN PLOT WINDOWS, AS YOU GO.
#Type Ctrl+C to cancel all.

import csv
import os
import glob
from matplotlib import pyplot as plt
import scipy.io
from skimage.feature import match_template
import numpy as np
import sys
import cv2
import pyvips
from array import *
import pyvips

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

if len(sys.argv) < 1:
	sys.exit('\nNo input file found. \n\nINPUT: filename.final.v')


#Get filepath and filenames
filepath = os.getcwd()
input_filename = sys.argv[1].rstrip('.final.v')
#can change the ASD macbeth filenames if necessary, otherwise looks for '1.txt', '2.txt'...'24.txt'.
macbeth_filenames = [str(i)+'.txt' for i in range(1,25)]

#if find(input_filename+'.RGB16.v', filepath) == None:
#	sys.exit('\nCannot find colour image. Looking for `filename.RGB16.v\' somewhere in same directory.')
	
if find(macbeth_filenames[0], filepath) == None:
	sys.exit('\nCannot find ref spectra for macbeth chart. Looking for `1.txt\'...`24.txt\' somewhere in directory.')

#Prisms wavelengths
wl_PR = (400, 450, 500, 550, 600, 650, 700, 750, 800, 850)

colours = ['dark_skin', 'light_skin', 'blue_sky', 'foliage', 'blue_flower', 'bluish_green',
           'orange', 'purplish_blue', 'moderate_red', 'purple', 'yellow_green', 'orange_yellow',
           'blue', 'green', 'red', 'yellow', 'magenta', 'cyan', 'white', 'neutral_8', 'neutral_6.5',
           'neutral_5', 'neutral_3.5','black']

#open PRISMS processed image files
vips_img = pyvips.Image.new_from_file(sys.argv[1], access='sequential')
clr_img = pyvips.Image.new_from_file(input_filename+'.RGB16.v', access='sequential')
clr_img_scl = clr_img.scaleimage()

#make jpeg of colour image
clr_img_scl.jpegsave(input_filename+'.jpeg')

#Select ROI for spectrum:
fromCenter = False
im = cv2.imread(input_filename+'.jpeg')
height, width, depth = im.shape
resized = cv2.resize(im, (width//2, height//2))
print('SELECT RECTANGLE CONTAINING MACBETH CHART...')
r = cv2.selectROI(input_filename, resized, fromCenter) # r = x, y, xw, yh

#Extract macbeth_chart from image file
mb_chart_area = vips_img.extract_area(2*r[0], 2*r[1], 2*r[2], 2*r[3]) #(left, top, width, height) or (x1, y1, x2-x1, y2-y1)
im = cv2.rectangle(im, (2*r[0], 2*r[1]), (2*r[0]+2*r[2], 2*r[1]+2*r[3]), (255,0,0), 2)

#therefore
tl = 2*r[0], 2*r[1] # x1, y1
br = 2*r[0]+2*r[2], 2*r[1]+2*r[3] # x2, y2
   
print('tl = ', tl)
print('br = ', br)
   
#across
a1= tl[0]
a2 = br[0]
#down
d1 = tl[1]
d2 = br[1]

#find each point on colour chart for the 24 colours
mb_colours_x = [] #(ACROSS)
mb_colours_y = [] #(DOWN)
# this is the centre of the first colour patch
a = a1+((a2-a1)//12)+5
d = d1+((d2-d1)//8)+5   

for j in range(4):
	a = a1+((a2-a1)//12)+5
	for i in range(6):
		mb_colours_x.append(a)
		mb_colours_y.append(d)
		a+=((a2-a1)//6)
	d+=((d2-d1)//4)

for j in range(len(colours)):
	print('Processing ', colours[j])
	x = mb_colours_x[j]
	y = mb_colours_y[j]
	im = cv2.rectangle(im, (mb_colours_x[j]-2, mb_colours_y[j]-2), (mb_colours_x[j]+2, mb_colours_y[j]+2), (0,0,255), 2)

	#Extract area from Target 
	Tarea = vips_img.extract_area(x-2, y-2, 5, 5) #(left, top, width, height)
	Tstats = Tarea.stats()        
	#Construct the mean array from the vips format double image object (containing stats). Column 5 is Mean avg. 
	Refl_PR = [(Tstats(4,k)[0]) for k in range(1,11)] 
	#open correct ASD spectrum
	xASD, yASD=np.loadtxt(find(macbeth_filenames[j], filepath), skiprows=1,unpack=True)
	#plots spectra for each colour
	axes = plt.gca()
	axes.set_xlim([350, 950])
	axes.set_ylim([0,1.2])
	plt.xlabel('Wavelength (nm)')
	plt.ylabel('Reflectance')
	plt.title(colours[j])
	plt.plot(wl_PR, Refl_PR, 'r+', label='PRISMS')
	plt.plot(xASD, yASD, label='ref.', color = 'blue')
	plt.legend(shadow=True)
	plt.show()
cv2.imwrite(input_filename+'_patches.png',im)	
    