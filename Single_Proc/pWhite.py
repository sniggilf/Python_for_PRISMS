
#INPUT 
#WHITE_IN.v (DARK_IN.v) (FLAT_IN.v)
#The optional arguments can be in any order but filename MUST contain the word 'dark' or 'flat'.

#OUTPUT (placed in PROC folder)
#Image.align.v
#Image.mat
#Image.mean.dat
#Image.mean.mat

#EXTERNAL DEPENDENCIES
#!! These files must be in the same filepath, or in any folder in same filepath, as pWhite.py!!
#dist.dat: a file containing the distance calibration data | hardcoded in readheader function
#instdark.v: a file containing a dark for dark simulation

import random
import subprocess
import sys
import string
import math
import numpy as np
import ntpath
import pyvips
import os
import time
import cv2


from array import *
from ctypes import *
from subprocess import call, Popen, PIPE

def readheader (datfile):	
	dd   = 0.4
	da   = 0.05
	db   = 0.37
	fp   = 0
	intt = []
	az = 0
	dist =0
    #make a list of the integration times from the dat file
	with open(datfile,'r') as f:
		data = f.readlines()
		for line in data:
			sp = line.split()			
			if len(sp)>0:				
				if sp[0] == 'Exposure':					
					intt.append(float(sp[2]))	
				if sp[0] == 'Focus:':
					fp = float(sp[1])			
				if sp[0] == 'Azimuth:':
					az = float(sp[1])
	#Find the distance from the distance calibration file	
	df = 1000
	with open(distfile,'r') as f:		
		data = f.readlines()		
		for line in data:
			sp = line.split()			
			if df > abs(float(fp)-float(sp[0])):
				df = abs(float(fp)-float(sp[0]))
				dist = float(sp[1])
	#Calculate light distance	
	dl = math.sqrt(pow((dist - da),2) + pow(dd,2) - 2 * dd * (dist-da) * math.cos((90+az)*math.pi/180)) - db
	#return the equivalent of .dat1 (ie, filter - integration time)
	if len(intt) != 10: print('!The dat file'+datfile+' does not contain 10 filters!')
	return intt, dl

def normmatrix(intt, outf):
	#create a matrix	
	with open(outf+'.mat','w') as of:
		of.write('10 10 1 0\n')		
		it = intt  ## exposure time for each filter
		for i in range (0,10):
			l = ['0 ','0 ','0 ','0 ','0 ','0 ','0 ','0 ','0 ','0 '] #base line
			l[i] = str(float(1/float(it[i])))#1/exposuretime
			#of.write(string.join(l,' ')+'\n ')
			of.write(' '.join(l)+'\n ')
	return

#find files
def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

start_time = time.time()

#Get filepath and filenames
raw_path = os.getcwd()
input_name = sys.argv[1].rstrip('.v')
distfile = find('dist.dat',raw_path)

#provide defaults
flatcal = False
darkcal = False
flatfile = 'None'
darkfile = 'instdark.v'

#Replace dark and flat files, if provided
for arg in sys.argv:
	if 'dark' in arg.lower():
		darkfile = arg
		darkcal = True
	if 'flat' in arg.lower():
		flatfile = arg
		flatcal = True

#Create output directory, 'PROC'
OP = os.path.join(raw_path, 'PROC\\')
if not os.path.exists(OP):
   os.makedirs(OP)

#Load external data
white = pyvips.Image.new_from_file(sys.argv[1], access='sequential')
dark_in = pyvips.Image.new_from_file(find(darkfile, raw_path), access='sequential')
if flatcal == True: flat = pyvips.Image.new_from_file(find(flatfile, raw_path), access='sequential')

#Start position and size of image to embed for shifting
x0=40
y0=40
xw=1450
yw=1150

print('-------------------- Processing white ---------------------------')
print('File:',input_name)

print('Dark: ', darkfile)
print('Flat: ', flatfile)		

#Read header and calculate counts/sec
wdist = 0
wdat, wdist = readheader(raw_path + '\\' + input_name + '.dat') ## wdat is intergration time again

#change  --- Using Lens and not telescope? adapt so that it doesn't need to be changed.
wdist=0
#change

if wdist <=0: print('!The lens was used. No info about distances!')
else: print('White standard distance to light = ',wdist,'m')

#Calculate mat
normmatrix(wdat,OP+input_name) 

cor = 1

#Load the target.mat file generated previously
mat = pyvips.Image.new_from_file(OP+input_name+'.mat') 

#simulate the dark for given integration times
facset = []
for i in range(0,10):
	facset.append(float(float(wdat[i]))*0.00093669);

#Calculates the dark for each channel (if instdark is used)
if darkcal == True: dark = dark_in
else: dark = dark_in.linear([1,1,1,1,1,1,1,1,1,1],facset)

#Subtract the dark from the white image
white_dark = white.subtract(dark)

#Recombine
white_rec0=white_dark.recomb(mat)  

#Flat field
if flatcal == True: white_rec=white_rec0.divide(flat)
else: white_rec=white_rec0

#Find shifts between channels
bands = []
for i in range(0,10):
	bands.append(white_rec.extract_band(i))

#-----------------------------------------------------------------------
#Find overlap between channels
xshift = []
yshift = []

overlap = 100

ref = bands[5]
					 
for i in range(0,10):
	img = bands[i]
	join, optional = ref.mosaic(img, 'horizontal', 0, 0, 0, 0, harea=10, bandno=0, dx0=True, dy0=True)	
	print('shifts for filter',i+1,' = ',optional['dx0'],optional['dy0'])     		
	xshift.append(optional['dx0'])
	yshift.append(optional['dy0'])

#-----------------------------------------------------------------------

#Align the channels
ch = []
for i in range(0,10):
	xx = float(x0)-float(xshift[i])
	yy = float(y0)-float(yshift[i])	
	ch.append(bands[i].embed(int(xx),int(yy),xw,yw, extend='black'))

print('Making aligned multispectral image ...')
final = ch[0]
for i in range(1,10):	
	final = final.bandjoin(ch[i])

final.write_to_file(OP+input_name+'.align.v')

#Recombine
align = final.linear([cor,cor,cor,cor,cor,cor,cor,cor,cor,cor],[0,0,0,0,0,0,0,0,0,0])


#ROI for White stats (can replace with manual selection below)
#x = 598
#y = 492
#xw = 270
#yh = 268
#r = (x,y,xw,yh)

#Manual selection:
############################################
white_scl = ch[5].scaleimage()
#make jpeg of colour image
white_scl.jpegsave('im_check.jpeg') 
fromCenter = False
imwh = cv2.imread('im_check.jpeg')
r = cv2.selectROI(imwh, fromCenter) # r = x, y, xw, yh


#Extract area from white tile
Warea = align.extract_area(r[0], r[1], r[2], r[3]) #(left, top, width, height)
Wstats = Warea.stats()
W=[]
        
#Construct the mean array from the vips format double image object (containing stats). Column 5 is Mean avg. 
for i in range(1,11):
        W.append(Wstats(4,i)[0])
		
        
#Extract column 0,5
with open(OP+input_name+'.mean.dat','w') as wf:
	for i in range(0,10):
		wf.write('{0} {1}\n'.format(str(i+1),str(W[i])))

##-----------------------------------------------------------------
		
###Run norm-matrix on the above
normmatrix(W, OP+input_name+'.mean')

print('All done')
print('-----------------------------------------------------------------')

print("--- Time = %s seconds ---" % (time.time() - start_time))

