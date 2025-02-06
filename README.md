# gptools

Tools to extract all free energy related info from gaussian output and goodvibes, and apply entropy scaling for better free energy in solvent.

## Author and Version

Author: Zihao Ye, Alexander Maertens  
Version: v0.0.2  
Date: 25/02/05  

## Environment Setup, Installation and Test

2 dependencies are required: pandas & goodvibes
Could be done by:
```
conda create -n gptools python=3.10 -y
conda activate gptools
conda install pandas -y
pip install goodvibes
```

Then, change to current folder ('/your/path/gptools/'), run:
```
pip install -e .
```

Finally, go to test file folder ('/your/path/gptools/test/'), run:
```
python -m gptools -s -g
```
Compare the `gauprocess.csv` with `gauprocess_template.csv` to see if they are the same.

If so, you are ready to use gptools!

## Usage

0. Move all your gaussian output files need to be processed into a single folder.
1. (In that folder) Run `python -m gptools` to process all the files.
2. Open `gauprocess.csv` in the same folder to get results.

You can also run in terminal:
```
python -m gptools -h
```
to get all the options and explaination.

Note: You would have free energy corrected by both goodvibes and entropy scaling by ```python -m gptools -g -s```.

## Explaination of Output Files and Some Important Details

### Basic

Command: `python -m gptools`
Output: 
- `file_name`: file name of the processed file (without suffix)
- `status`: if this file have terminate normally (Normal or Error/Running)
- `E`: electron energy from gaussian output file
- `G_corr`: free energy correction (G-E) directly from gaussian output file
- `G`: free energy directly from gaussian output file
- `num_imag`: number of imaginary frequencies from gaussian output file
- `freq_cons`: first frequency constant (largest for imag. and smallest for real.)
- `opt_points`: how many steps have been optimized (exist only for Error/Running files)
- `converge`: converge status of the job, number stands for number of the 'YES' at the last step (exist only for Error/Running files) 

### With goodvibes only

Command: `python -m gptools -g`
Output (besides basic): 
- `ZPE`: file name of the processed file (without suffix)
- `H_corr`: enthalpy correction (H-E) from goodvibes output
- `H`: enthalpy from goodvibes output
- `T.qh-S_tot`: T.qh-S from goodvibes output
- `qh-G_corr`: qh corrected free energy correction (qh-G-E) from goodvibes output
- `qh-G`: qh corrected free energy from goodvibes output

Note: goodvibes is invoked with 1M as standard state!

### With entropy terms only

Command: `python -m gptools -s`
Output (besides basic): 
- `S_tot`: total entropy from gaussian file (S_tot = S_elec + S_trans + S_rot + S_vib)
- `S_elec`: electron entropy from gaussian file
- `S_trans`: translational entropy from gaussian file
- `S_rot`: rotational entropy from gaussian file
- `S_vib`: vibrational entropy from gaussian file

### With solvent free energy correction (both goodvibes and entropy terms)

Command: `python -m gptools -g -s`
Output (besides mentioned above): 
- `solv-G_corr`: qh and entropy scaling corrected free energy correction (solv-G-E)
- `solv-G`: qh and entropy scaling corrected free energy

Note: now scaling method is 50% of S_trans and S_rot and S_elec, maybe support different later
