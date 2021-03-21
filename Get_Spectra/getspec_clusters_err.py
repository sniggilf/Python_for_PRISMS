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
from scipy.ndimage import gaussian_filter

from array import *

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
dtype_to_format = {
    'uint8': 'uchar',
    'int8': 'char',
    'uint16': 'ushort',
    'int16': 'short',
    'uint32': 'uint',
    'int32': 'int',
    'float32': 'float',
    'float64': 'double',
    'complex64': 'complex',
    'complex128': 'dpcomplex',
}
# map vips formats to np dtypes
format_to_dtype = {

    'uchar': np.uint8,

    'char': np.int8,

    'ushort': np.uint16,

    'short': np.int16,

    'uint': np.uint32,

    'int': np.int32,

    'float': np.float32,

    'double': np.float64,

    'complex': np.complex64,

    'dpcomplex': np.complex128,

}
def vips2numpy(vi):

    return np.ndarray(buffer=vi.write_to_memory(),

                      dtype=format_to_dtype[vi.format],

                      shape=[vi.height, vi.width, vi.bands])
def numpy2vips(a):
    height, width, bands = a.shape
    linear = a.reshape(width * height * bands)
    vi = pyvips.Image.new_from_memory(linear.data, width, height, bands,
                                      dtype_to_format[str(a.dtype)])
    return vi


#USER CAN CHANGE FOR LARGER/SMALLER IMAGES
n_zoom = 2 # ok for PRISMS dimensions

if len(sys.argv) < 3:
	sys.exit('\nNo output filename given for spectrum (e.g. \'red1\'). \n\nINPUT: filename.final.v OUTPUT_NAME')

#Get filepath and filenames
filepath = os.getcwd()
input_filename = sys.argv[1].rstrip('.final.v')
output_filename = sys.argv[2]

#open image files
vips_img = pyvips.Image.new_from_file(sys.argv[1], access='sequential')
clr_img = pyvips.Image.new_from_file(input_filename+'.RGB16.v', access='sequential')

#if cluster map is different size to original image cube
#vips_img = vips_img.resize(0.5)
#clr_img = clr_img.resize(0.5)

#optional cluster map 
cluster_no=1
if len(sys.argv) > 3:
	map_img = pyvips.Image.new_from_file(sys.argv[3], access='sequential')
	cluster_no = input('Give cluster number to use :  \n')

	cluster_no = int(cluster_no)
	map_array = vips2numpy(map_img)
	if cluster_no == 0: 
		map_array[map_array ==0] = 500 
		cluster_no=500
		map_array[map_array != cluster_no] = 0 
	else:
		map_array[map_array != cluster_no] = 0 
	#no_pixels_used = np.count_nonzero(map_array)
	mask = map_array/cluster_no
	mask_img = numpy2vips(mask)
	cluster_map = mask_img.multiply(vips_img)



no_bands = vips_img.bands
clr_img_scl = clr_img.scaleimage()
#make jpeg of colour image
clr_img_scl.jpegsave(input_filename+'_RGB.jpeg')

#Create output directory, 'SPEC'
OP = os.path.join(filepath, 'SPEC\\')
if not os.path.exists(OP):
   os.makedirs(OP)

#Prisms wavelengths
wl_PR = (400, 450, 500, 550, 600, 650, 700, 750, 800, 850)

#extract bands from image cube
bands = []
for i in range(len(wl_PR)):
	bands.append(vips_img.extract_band(i))

#Select ROI for spectrum:
fromCenter = False
im = cv2.imread(input_filename+'_RGB.jpeg')
height, width, depth = im.shape
resized = cv2.resize(im, (width//n_zoom, height//n_zoom))
r = cv2.selectROI(input_filename, resized, fromCenter) # r = x, y, xw, yh

#Extract area from white tile
Warea = cluster_map.extract_area(n_zoom*r[0], n_zoom*r[1], n_zoom*r[2], n_zoom*r[3])#r[0], r[1], r[2], r[3]) #(left, top, width, height)
mask_area = mask_img.extract_area(n_zoom*r[0], n_zoom*r[1], n_zoom*r[2], n_zoom*r[3])
tot_no_pixels_selected = n_zoom*r[2]*n_zoom*r[3]
maskarea_array = vips2numpy(mask_area)
no_pixels_used = np.count_nonzero(maskarea_array)
print('tot no. pixels selected:', tot_no_pixels_selected)
print('no pixels used :', no_pixels_used)
Wstats = Warea.stats()
W=[]
Stdev = []      
#Construct the mean array from the vips format double image object (containing stats). Column 5 is Mean avg. 
for i in range(1,len(wl_PR)+1):
	selection_mean = (Wstats(4,i)[0])*tot_no_pixels_selected/no_pixels_used
	W.append(selection_mean)
for i in range(1,len(wl_PR)+1):
        Stdev.append(Wstats(5,i)[0])

cluster_ll = [W[i]-Stdev[i] for i in range(len(wl_PR))]
cluster_ul = [W[i]+Stdev[i] for i in range(len(wl_PR))]

cv2.rectangle(im, (n_zoom*r[0], n_zoom*r[1]), (n_zoom*r[0]+n_zoom*r[2], n_zoom*r[1]+n_zoom*r[3]), (255,0,0), 2)
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
		
		xref, yref, stdev_ref = np.loadtxt(find(r, filepath), delimiter='\t', skiprows=data_row ,unpack=True)##<- change skiprows if data contains header

		#axes.set_xlim([380, 900])
		axes.set_ylim([0,1.1])
		plt.xlabel('Wavelength (nm)')
		plt.ylabel('Reflectance')
		#based on no. data points, uses circles (e.g. PRISMS) or line (e.g. FORS)
		if len(xref) <=1 :
			#print(filetype)
			plt.plot(xref, yref, 'o', mfc='none', label=filetype)#r.rstrip('.'+filetype))#, color = 'blue')
		else: 
			#print(filetype)
			plt.plot(xref, yref, label=filetype)#r.rstrip('.'+filetype))
			plt.fill_between(xref, yref-stdev_ref, yref+stdev_ref,
					alpha=0.2)#, edgecolor=colours_new[i], facecolor=colours_new[i], antialiased=True)
	plt.plot(wl_PR, W, label = output_filename)
	plt.fill_between(wl_PR, cluster_ll, cluster_ul,
		alpha=0.2)
	plt.legend(shadow=True)
	plt.show()
	fref.savefig(OP+output_filename, bbox_inches='tight')
else:
	f = plt.figure()
	axes = plt.gca()
	#axes.set_xlim([xmin,xmax])
	axes.set_ylim([0,1.0])
	plt.xlabel('Wavelength, nm')
	plt.ylabel('Reflectance')
	plt.plot(wl_PR, W)#gaussian_filter(W, sigma=1.), 'r')
	plt.fill_between(wl_PR, cluster_ll, cluster_ul,
		alpha=0.2)
	plt.show()
	f.savefig(OP+output_filename, bbox_inches='tight')


#record refl spectrum for ROI
with open(OP+output_filename+'.txt','w') as wf:
	for i in range(0,no_bands):
		wf.write('{0}\t {1}\t {2}\n'.format(str(wl_PR[i]),str(W[i]), str(Stdev[i])))

