#INPUT 
#TARGET_IN.V WHITE_IN.v (DARK_IN.v) (FLAT_IN.v)
#The optional arguments can be in any order, but filename MUST contain the word 'dark' or 'flat'.

#OUTPUT
#TARGET_IN.final.v : aligned multispectral image
#TARGET_IN.XYZD65.v: aligned XYZ colour image for 2deg observer under D65 illuminant
#TARGET_IN.RGB16.V: 16 bit rgb image (if you want)

#EXTERNAL DEPENDENCIES
#!! These files must be in, or in any folder within, the same location as pTarget.py !!
#dist.dat: a file containing the distance calibration data | hardcoded in readheader function
#instdark.v: a file containing a dark for dark simulation
#CIED65.txt : Power spectrum of the D65 (Daylight) illuminant 
#CIE_2degObs.txt : colour matching functions, x,y,z, for a 2degree observer

import random
import subprocess
import sys
import string
import math
import numpy as np
import ntpath
import os
import pyvips

import matplotlib.pyplot as plt
import time

from array import *
from ctypes import *
from subprocess import call, Popen, PIPE
from scipy.interpolate import PchipInterpolator


def readheader (datfile):	
	dd   = 0.4
	da   = 0.05
	db   = 0.37
	fp   = 0
	intt = []
	az = 0
	dist = 0
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
			of.write(' '.join(l)+'\n ')
	return

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

start_time = time.time()
			
#Get filepath and filenames
raw_path = os.getcwd()
input_name = sys.argv[1].rstrip('.v')
input_white = sys.argv[2].rstrip('.v')

#find external dependencies in filepath
CIE_D65 =find('CIE_D65.txt', raw_path)
CIE_2deg = find('CIE_2degObs.txt', raw_path)
distfile = find('dist.dat', raw_path)

#provide defaults
flatcal = False
darkcal = False
flatfile = 'None'
darkfile = 'instdark.v'

#update dark and flat files, if provided
for arg in sys.argv:
	if 'dark' in arg.lower():
		darkfile = arg
		darkcal = True
	if 'flat' in arg.lower():
		flatfile = arg
		flatcal = True
	
#Creates output directory 'PROC'
OP = os.path.join(raw_path, 'PROC\\')
if not os.path.exists(OP):
   os.makedirs(OP)

#Load external data
targ = pyvips.Image.new_from_file(sys.argv[1], access='sequential')
dark_in = pyvips.Image.new_from_file(find(darkfile,raw_path), access='sequential')

if flatcal == True: flat = pyvips.Image.new_from_file(find(flatfile, raw_path), access='sequential')

Wmat = pyvips.Image.new_from_file(OP+input_white+'.mean.mat')

#Start position and size of image to embed for shifting
x0=40
y0=40
xw=1450
yw=1150


print('--------------------- Processing target -------------------------')
print('Image:',input_name)

print('Dark = ', darkfile)
print('Flat: ', flatfile)


#process target dat file
ldist =0
tdat1,ldist = readheader(raw_path+'\\'+input_name+'.dat')

#change
ldist =0
#change

if ldist ==0: print('!The lens was used: no information about target and white positions!')
else: print('Target distance to light  = ', ldist, 'm')
#process white dat file
wdist =0
wdat1,wdist = readheader(raw_path+'\\'+input_white+'.dat')

#change --- if need 3d info and are using dist.dat
wdist = 0
#change --- 

if wdist !=0: print('White distance to light   = ',wdist,'m')

#run norm-matrix on the target
normmatrix(tdat1,OP+input_name)

#Load the target.mat file generated previously
mat = pyvips.Image.new_from_file(OP+input_name+'.mat')

#calculate correction factor for the white
if ldist>0 and wdist>0: cor = pow(ldist,2)/pow(wdist,2)
else: cor = 1
print('Distance correction factor= ', cor)

#simulate the dark for given integration times
facset = []
for i in range(0,10):
	facset.append(float(tdat1[i])*0.00093669);	

#Calculate the dark for each channel (if instdark is used)
if darkcal == True: dark = dark_in
else: dark = dark_in.linear([1,1,1,1,1,1,1,1,1,1],facset)

#Subtract the dark from the target image
targ_dark = targ.subtract(dark)

#Recombine image
targ_rec0 = targ_dark.recomb(mat)

#flat field
if flatcal == True: targ_rec = targ_rec0.divide(flat)
else: targ_rec = targ_rec0


#Find shifts between channels
bands = []
for i in range(0,10):
	bands.append(targ_rec.extract_band(i))

xshift = []
yshift = []

dx0 =0
dy0 =0

overlap = 100

ref = bands[5]
for i in range(0,10):
	img = bands[i]
	join, optional = ref.mosaic(img, 'horizontal', 0, 0, 0, 0, harea=50, bandno=0, dx0=True, dy0=True)	
	print('shifts for filter',i+1,' = ',optional['dx0'],optional['dy0'])     		
	xshift.append(optional['dx0'])
	yshift.append(optional['dy0'])

#Align the channels
ch = []
for i in range(0,10):
	xx = float(x0)-float(xshift[i])
	yy = float(y0)-float(yshift[i])	
	ch.append(bands[i].embed(int(xx),int(yy),xw,yw, extend='black'))

print('Making aligned multispectral image ...')
align = ch[0]
for i in range(1,10):		
	align = align.bandjoin(ch[i])		

#Recombine image
f1 = align.recomb(Wmat)
final = f1.linear([cor,cor,cor,cor,cor,cor,cor,cor,cor,cor],[0,0,0,0,0,0,0,0,0,0])

##correct for scattering ----------
#corS=1.1
#corC=-0.056
#final = f1.linear([corS,corS,corS,corS,corS,corS,corS,corS,corS,corS],[corC,corC,corC,corC,corC,corC,corC,corC,corC,corC])
##the above needs to be changed for different capture geometry -------

#Write out final aligned multispectral image
final.write_to_file(OP+input_name+'.final.v')


#make the colour images
print('Making the colour image ...')
colstarttime = time.time()

bands = []
for i in range(0,10):
	bands.append(final.extract_band(i))

#bands used for colour image (880nm not in range of CIE standards)
wl_PR = (400, 450, 500, 550, 600, 650, 700, 750, 800, 850)

#create new wavelengths to match standards and be within PRISMS range(400, 405,... 830nm)
wl_new = np.arange(400, 835, 5)
wl_PR = wl_new


#CIE standards data
wl_D65, I_D65 = np.loadtxt(CIE_D65, unpack=True)
wl_2deg, xbar, ybar, zbar = np.loadtxt(CIE_2deg, unpack=True)

#interpolation of CIE standard data. Function given at set wavelengths, wl_PR, according to PRISMS filters
D65_int = PchipInterpolator(wl_D65, I_D65, extrapolate=False)(wl_PR)
xbar_int = PchipInterpolator(wl_2deg, xbar, extrapolate=False)(wl_PR)
ybar_int = PchipInterpolator(wl_2deg, ybar, extrapolate=False)(wl_PR)
zbar_int = PchipInterpolator(wl_2deg, zbar, extrapolate=False)(wl_PR)

#k = Scale factor K/N 
kn = 100/sum(D65_int*ybar_int)
#Src, Spectral power of the Illuminant (D65 daylight) x obs, colour matching function of 2deg observer( for x, y and z).
srcobs_x = D65_int*xbar_int
srcobs_y = D65_int*ybar_int
srcobs_z = D65_int*zbar_int


#interpolate image cube to match intervals i wavelength given as above...
cnt =0
newbands = []
for i in range(9):
	#print('Making new bands between bands %s and %s' %(i, i+1))
	for j in range(10):
		#print('New bands %s ...' %(cnt))
		newband = (bands[i+1]-bands[i])*j/10 + bands[i]
		newbands.append(newband)
		cnt+=1
#print('New bands %s ...' %(cnt))
newbands.append(bands[9])		
	

#for each waveband, multiply image by src*obs
img_Xn = [newbands[i]*srcobs_x[i] for i in range(len(wl_PR))]
img_Yn = [newbands[j]*srcobs_y[j] for j in range(len(wl_PR))]
img_Zn = [newbands[k]*srcobs_z[k] for k in range(len(wl_PR))]


#integrate over all wavelengths and multiply by scale factor to get X, Y, Z
imgX = pyvips.Image.sum(img_Xn)*kn
imgY = pyvips.Image.sum(img_Yn)*kn
imgZ = pyvips.Image.sum(img_Zn)*kn

#join X, Y, Z bands
imgC = imgX.bandjoin(imgY)
imgC = imgC.bandjoin(imgZ)

#if you want rgb image 
imgC_rgb = imgC.colourspace('rgb16', source_space = 'xyz')

#save XYZ colour image to vips image file.
imgC.vipssave(OP+input_name+'.XYZD65.v')

#save sRGB file
imgC_rgb.vipssave(OP+input_name+'.RGB16.v')

print('-----------------------------End---------------------------------')

print("--- Time = %s seconds ---" % (time.time() - start_time))

