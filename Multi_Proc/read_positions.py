#command:
# > python read_positions.py full_path_to_folder


import math
import sys
import numpy as np
import os
import pyvips
import glob

import matplotlib.pyplot as plt
import time


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
				if sp[0] == 'Altitude:':
					alt = float(sp[1])

	#return the equivalent of .dat1 (ie, filter - integration time)
	if len(intt) != 10: print('!The dat file'+datfile+' does not contain 10 filters!')
	return intt, alt, az, fp

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

#map np dtypes to vips
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
					  
def numpy2vips(a):
    height, width, bands = a.shape
    linear = a.reshape(width * height * bands)
    vi = pyvips.Image.new_from_memory(linear.data, width, height, bands,
                                      dtype_to_format[str(a.dtype)])
    return vi
def vips2numpy(vi):
    return np.ndarray(buffer=vi.write_to_memory(),
                      dtype=format_to_dtype[vi.format],
                      shape=[vi.height*vi.width, vi.bands])

#Get filepath and filenames
#raw_path = os.getcwd()

filepath = sys.argv[1]
foldername = filepath.split('\\')[-1]

#distfile = find('dist.dat', raw_path)

   
with open(filepath+'\\3D.txt','w') as wf:
	wf.write('{0}\t{1}\t\t{2}\t\t{3}\n'.format('Filename', 'Altitude', 'Azimuth', 'Focus Position'))
	wf.write('---------------------------------------------------------------------------------------------------------\n')
	

#distfile = find('dist.dat', raw_path)

for file in glob.iglob(filepath+'\\*.dat'):
	filename = file.split('\\')[-1].strip('.dat')
	tdat1,alt_t, az_t, fp_t = readheader(file)
	with open(filepath+'\\3D.txt','a') as wf:
		wf.write('{0}\t{1}\t{2}\t{3}\n'.format(str(filename), alt_t, az_t, fp_t))





