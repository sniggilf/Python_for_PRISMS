Single Proc
------------------------------------------------------------------
Process single cubes at a time if need to include dark and/or flat field correction. 
First the white standard image is processed, then the image of the target is processed.

commands:
> python pWhite.py white_filename.v (dark_filename.v flat_filename.v)

then

> python pTarget.py target_filename.v white_filename.v (dark_filename.v flat_filename.v)

NOTE: The optional arguments (in parentheses) can be in any order but filename MUST contain the word 'dark' or 'flat'.

