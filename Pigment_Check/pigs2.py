#Quick comparison of spectrum with (linseed oil) pigment database for single chosen colour

#INPUT: filename colour 

#Note: 'filename' is name of your spectrum (e.g. red1.txt), 'colour' should be Blue, Green, Red, Yellow, Purple, White or Black.

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import sys

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

#Get filepath, files 
filepath = os.getcwd()
input_filename = sys.argv[1]
choose_colour = sys.argv[2]

#open spectrum
wl_sample, R_sample = np.loadtxt(find(input_filename, filepath), skiprows = 0, unpack=True)

#check colour input
colour = None
clrs = ['Blue', 'Green', 'Red', 'Yellow', 'Purple-White-Black']
for clr in clrs:
	if choose_colour.lower() in clr.lower(): colour = clr
if colour == None: 
	sys.exit('\nNo colour match found. \n\nINPUT: filename colour (Blue, Green, Red, Yellow)')

#open correct database sheet
df = pd.read_excel(find('ASD_LinseedOil_database.ods', filepath), sheet_name = colour)
pigs = list(df.columns)


for j in range(1, len(pigs)): ##
	axes = plt.gca()
	axes.set_xlim([900,2600])
	axes.set_ylim([0,1.1])
	plt.xlabel('Wavelength (nm)')
	plt.ylabel('Reflectance')   
	#if j%2 == 0 :
	print(j)
	plt.plot(df['Wavelength (nm)'][2:2000], df[pigs[j]][2:2000], label=pigs[j])
	plt.plot(wl_sample, R_sample, label=input_filename.split('.')[0])
	plt.legend(shadow=True)
	plt.show()
	#else: plt.plot(df['Wavelength (nm)'][2:2000], df[pigs[j]][2:2000], label=pigs[j]) 
