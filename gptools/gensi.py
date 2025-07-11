# generate SI .txt file
# Author: Zihao Ye
# creation time: Jun, 2025
# version: 2025/06/27

import os
import pandas as pd

from gjftools.gjftools import gjfdata


CSV_FILE = 'gauprocess.csv'
TXT_FILE = 'SI_coord.txt'

def gensi(log_dir: str=os.getcwd(),
          need_entropy: bool=False,
          need_goodvibes: bool=False) -> str:
    '''
    get all coords from a directory of log files and output to
    one xyz file for paste to the SI part of papers.
    '''
    error_count = 0

    enth_title = 'H_corr'  # enthalpy
    free_title = 'G_corr'  # no correction
    if need_goodvibes:
        free_title = 'qh-G_corr'  # only goodvibes correction
    if need_entropy and need_goodvibes:
        free_title = 'solv-G_corr'  # goodvibes and solvation correction

    # read csv file
    gp_df = pd.read_csv(CSV_FILE)
    file_col = 'file_name'
    # file_col = gp_df.columns['file_name']
    # gp_df_sp = gp_df[gp_df[file_col].str.endswith('_sp')]
    gp_df_opt = gp_df[~gp_df[file_col].str.endswith('_sp')]

    # go through all files
    total_SI_list = []
    for _, row in gp_df_opt.iterrows():
        opt_file = row[file_col]
        sp_file = f'{opt_file}_sp'
        # check files
        if sp_file not in list(gp_df[file_col]):
            print(f'{opt_file} does not have corresponding single point file!')
            error_count += 1
            continue
        if row['status'] != 'Normal':
            print(f'{opt_file} does not terminate normally!')
            error_count += 1
            continue
        # collect data
        ener = round(float(row['E']), 6)
        spe = round(float(gp_df[gp_df[file_col] == sp_file]['E'].iloc[0]), 6)
        enth = round(float(row[enth_title]) + spe, 6)
        free = round(float(row[free_title]) + spe, 6)
        single_txt_list = [
            f'{opt_file}\n',
            f'E={ener}\n',
            f'E_SP={spe}\n',
            f'H={enth}\n',
            f'G={free}\n',
        ]
        # collect imaginary freq if needed
        if row['num_imag'] != 0.0:
            single_txt_list.append(f'''Imag. Freq. {row['freq_cons']}\n''')
        # collect coords
        log_file = os.path.join(os.path.abspath(log_dir), f'{sp_file}.log')
        # read log
        _xyz = gjfdata()
        _xyz.get_body_from_log(log_file)
        # crude str list
        _crude_list = _xyz.write_xyz(to_str_list=True)
        # do some modification
        _crude_list[0] = f'charge and multiplicity: {_xyz.c_m}\n'  # add charge and multiplicity
        _crude_list[1] = 'Cartesian coordinates:\n'  # remove atom number
        _crude_list.append('\n')
        # combine str list
        single_txt_list.extend(_crude_list)

        # add this structure to the overall list
        total_SI_list.extend(single_txt_list)
    
    if error_count:
        print(f'Warning! {error_count} structures has error!')

    SI_coord_file = os.path.join(os.path.abspath(log_dir), TXT_FILE)
    with open(SI_coord_file, 'w') as coord:
        coord.writelines(total_SI_list)
    print(f'SI txt file has been generated to {TXT_FILE} in current folder!')
