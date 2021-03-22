Macbeth Auto
------------------

Program for quick rough check of entire macbeth chart as taken using PRISMS.
Select the entire macbeth chart when selecting ROI.

Command:
> python macbeth_auto.py filename.final.v     

Note: Directory must contain both XXXX.final.v and XXXX.RGB16.v 

OUTPUT: filename_patches.jpeg    (showing points at which reflectance spectra were sampled)

- Macbeth chart must have greyscale neutral colours on bottom line
- If macbeth chart is rotated slightly, some regions may not be selected properly - check output image.
- Exit each plot window as you go
- If wish to save spectral plots, save in window then exit as you go.
- Type Ctrl+C to cancel all.