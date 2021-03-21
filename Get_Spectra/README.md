Get Spec
-----------------------------------
command:

> python getspec.py XXXX.final.v OUTPUT

* With code in same dir as your data (including both RGB and final files), choose calibrated file (filename.final.v) to select
a ROI from for spectrum, and choose an OUTPUT name (e.g. red1).

	* After selecting ROI, press return.

* Choose whether you'd like to compare with a previously extracted spectrum (y/n).

	*If choosing a previously extracted spectrum give full name (e.g. red1.txt).

	*You can select multiple spectra to compare with (just list names e.g. > red1.txt red2.txt red3.txt)

*Plot will appear then exit by crossing the window if do not wish to save a manipulated version of the plot.

*Folder 'SPEC' will appear with spectrum, plot figure, and ROI selection image. Further spectra will be placed here.


Get Spec Err
-----------------------------------
command:

> python getspec_err.py XXXX.final.v OUTPUT

If using getspec_err.py, output spectra and plots will also contain standard deviations. 

Get Spec Clusters
-------------------------------------------
command: 
> python getspec_clusters_err.py XXXX.final.v OUTPUT clustermap_filename.v

clustermap_filename.v should be a clustermap, associated with XXXX.final.v, as output from one of our clustering codes and in vips format.

You will be asked which cluster number you choose to use before the selection of the ROI as above.