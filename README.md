# gptools

Tools to extract all free energy related info from gaussian output and goodvibes, and apply entropy scaling for better free energy in solvent.

## Author and Version

Author: Zihao Ye, Alexander Maertens  
Version: v0.0.5  
Date: 25/07/11

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
python -m gptools -s -g -c 1.5 -t 273.15
```
Compare the `gauprocess.csv` with `gauprocess_template.csv` to see if they are the same.

If so, you are ready to use gptools!

If you also want to test --gensi function (extra dependency of gjftools is needed), run:
```
python -m gptools -s -g -c 1.5 -t 273.15 --gensi
```
Compare the `SI_coord.txt` with `SI_coord_template.txt` to see if they are the same.

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

Extra keywords:
- `-t [298.15]`: temperature in K which is used by goodvibes (default 298.15 K)  
- `-c [1.0]`: concentration in M which is used by goodvibes (default 1.0 M)  

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

Scaling factor of S_trans and S_rot could be adjusted by `--factor_trans [float] ` and `--factor_rot [float] `, default value is 0.5 for both.

### Generate SI txt file
**Requirements:**  
This function cannot be used unless gjftools is also installed!  
All optimization files (with freq) should be accompied by a single point file with extra suffix "_sp".  
Also please change all .out file to .log file before using --gensi function to avoid errors!
For example: D-1-reactant.log & D-1-reactant_sp.log  

Command: `python -m gptools [-g] [-s] --gensi`  
Output:  
A txt file including SI results with format of:
```
D-1-Hex-4_6-Me-2-pyrimidone
E=-653.349033
E_SP=-654.058422
H=-653.732985
G=-653.790625
charge and multiplicity: 0 1
Cartesian coordinates:
C    -1.939343  -0.804694  -0.296330
C    -0.123427  0.776518  -0.153597
C    -0.937281  1.788189  0.186678
C    -2.044149  1.193569  -0.669656
H    -0.840745  2.703419  0.767000
...
```

