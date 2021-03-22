#Get reflectance spectrum of a region of interest
#INPUT:
#TARGET_IN.final.v OUTPUT_NAME
#
#OUTPUT:
#OUTPUT_NAME_ROI.jpeg    - Selected ROI 
#OUTPUT_NAME.pdf         - plotted Refl. Spectrum
#OUTPUT_NAME.dat         - data file for Refl. spectrum

# NOTE!
# For comparison with a reference spectrum, make sure you have ref spectrum 
# data file (e.g. 'vermilion.txt') somewhere in, or in a folder within, same directory as this program.
# Also make sure that data does not contain a header!

import os
import numpy as np
import sys
import cv2
import pyvips
import matplotlib.pyplot as plt
from array import *

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


if len(sys.argv) < 3:
	sys.exit('\nNo output filename given for spectrum (e.g. \'red1\'). \n\nINPUT: filename.final.v OUTPUT_NAME')

#Get filepath and filenames
filepath = os.getcwd()
input_filename = sys.argv[1].rstrip('.final.v')
output_filename = sys.argv[2]

#open image files
vips_img = pyvips.Image.new_from_file(sys.argv[1], access='sequential')
clr_img = pyvips.Image.new_from_file(input_filename+'.RGB16.v', access='sequential')

clr_img_scl = clr_img.scaleimage()
#make jpeg of colour image
clr_img_scl.jpegsave(input_filename+'.jpeg')

#Create output directory, 'SPEC'
OP = os.path.join(filepath, 'SPEC\\')
if not os.path.exists(OP):
   os.makedirs(OP)

#Prisms wavelengths
wl_PR = (400, 450, 500, 550, 600, 650, 700, 750, 800, 850)

#extract bands from image cube
bands = []
for i in range(0,10):
	bands.append(vips_img.extract_band(i))

#Select ROI for spectrum:
#test = bands[4].scaleimage()
#test.jpegsave('im_spec_select.jpeg') 
fromCenter = False
im = cv2.imread(input_filename+'.jpeg')
height, width, depth = im.shape
resized = cv2.resize(im, (width//2, height//2))
r = cv2.selectROI(input_filename, resized, fromCenter) # r = x, y, xw, yh

#Extract area from white tile
Warea = vips_img.extract_area(2*r[0], 2*r[1], 2*r[2], 2*r[3]) #(left, top, width, height)
Wstats = Warea.stats()
W=[]
        
#Construct the mean array from the vips format double image object (containing stats). Column 5 is Mean avg. 
for i in range(1,11):
        W.append(Wstats(4,i)[0])


cv2.rectangle(im, (2*r[0], 2*r[1]), (2*r[0]+2*r[2], 2*r[1]+2*r[3]), (255,0,0), 2)
cv2.imwrite(OP+output_filename+'_ROI.png',im)	
cv2.destroyAllWindows()
		
# To compare with reference Spectrum
comp = False
compare = input('Compare with other spectra? (y/n)  \n')

if compare.lower() == 'y' : 
	comp = True
	ref_spec = input('Give full filename(s) (e.g. red1.txt) :  ')
	refs = ref_spec.split()
	
	fref = plt.figure()
	axes = plt.gca()
	for r in refs:
		filetype = r.split('.')[0]#e.g '.dat' or '.txt'
		fname = find(r, filepath)
		lines = [line.split()[0] for line in open(fname)]
		#print('First line:', lines[0])
		for linno, lin in enumerate(lines):
			try:
				val = float(lin)
				print('-----%s----- \n Data begins :  line %s \n' % (r, linno))
				data_row = linno
				break
			except:
				print('')
		
		xref, yref = np.loadtxt(find(r, filepath), delimiter='\t', skiprows=data_row ,unpack=True)##<- change skiprows if data contains header

		axes.set_xlim([380, 900])
		axes.set_ylim([0,1.1])
		plt.xlabel('Wavelength (nm)')
		plt.ylabel('Reflectance')
		#based on no. data points, uses circles (e.g. PRISMS) or line (e.g. FORS)
		if len(xref) <=10 :
			#print(filetype)
			plt.plot(xref, yref, 'o', mfc='none', label=filetype)#r.rstrip('.'+filetype))#, color = 'blue')
		else: 
			#print(filetype)
			plt.plot(xref, yref, label=filetype)#r.rstrip('.'+filetype))
	plt.plot(wl_PR, W, 'r+', label = output_filename)
	plt.legend(shadow=True)
	plt.show()
	fref.savefig(OP+output_filename, bbox_inches='tight')
else:
	f = plt.figure()
	axes = plt.gca()
	#axes.set_xlim([xmin,xmax])
	axes.set_ylim([0,1.1])
	plt.xlabel('Wavelength, nm')
	plt.ylabel('Reflectance')
	plt.plot(wl_PR, W, 'r+')
	plt.show()
	f.savefig(OP+output_filename, bbox_inches='tight')


#record refl spectrum for ROI
with open(OP+output_filename+'.txt','w') as wf:
	for i in range(0,10):
		wf.write('{0}\t {1}\n'.format(str(wl_PR[i]),str(W[i])))

