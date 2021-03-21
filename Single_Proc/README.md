Single Proc
------------------------------------------------------------------
Process single cubes at a time if need to include dark and/or flat field correction

commands:
> python pWhite.py white_filename.v (dark_filename.v flat_filename.v)
> python pTarget.py target_filename.v white_filename.v (dark_filename.v flat_filename.v)

#NOTE: The optional arguments (in parentheses) can be in any order but filename MUST contain the word 'dark' or 'flat'.

