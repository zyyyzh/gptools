# collect and process gaussian output file
# Author: Zihao Ye
# creation time: Dec, 2022
# version: 2025/02/01

import os
import re
import sys
import csv
import argparse
import subprocess

from gptools.extractors import (
    get_status,
    get_sp_energy,
    get_free_energy,
    get_imag_freq,
    get_entropy,
    get_opt_points,
    get_converge,
    extract_goodvibes_result,
    get_solv_corr,
)
from gptools.utils import merge_and_update

import pandas as pd


def process(work_dir: str=os.getcwd(),
            need_entropy: bool=False,
            need_goodvibes: bool=False,
            temp: float=298.15,
            ):
    '''
    process all log or out file in work_dir
    determine whether they are normal termination
    if normal termination,
        get single point energy (HF=)
        get gibbs free energy correction and free energy
        get entropies (upon request)
        run goodvibes and use new free energies (upon request)
    if running or error,
        get optimization points
        get converge status
    output to a csv file
    '''
    # find output file
    gau_list = [file for file in os.listdir(work_dir)
                if file.endswith('.log') or file.endswith('.out')]
    gau_list.sort()

    # initialize data strucutre 
    data_list = []

    # start processing
    print(f'Temperature used is {temp}K!')
    print('Extracting data from gaussian output!')
    for file in gau_list:
        gau_file = os.path.abspath(work_dir + '/' + file)
        with open(gau_file) as f:
            gauf = f.readlines()
        # normal termination
        if get_status(gauf): 
            data_dict = {'file_name': file.split('.')[0], 'status': 'Normal'}
            data_dict.update(get_sp_energy(gauf))
            data_dict.update(get_free_energy(gauf))
            # has freq calculation
            if (data_dict['G'] != 0.0) or (data_dict['G'] != -1.0):
                data_dict.update(get_imag_freq(gauf))
                if need_entropy:
                    data_dict.update(get_entropy(gauf))
            # no freq calculation
            else:
                data_dict.update({'num_imag': -1, 'freq_cons': 0.0})
                if need_entropy:
                    data_dict.update({'S_tot': -1.0, 'S_elec': -1.0, 
                        'S_trans': -1.0, 'S_rot': -1.0, 'S_vib': -1.0})

        else:  # abnormal termination or running
            data_dict = {'file_name': file.split('.')[0], 'status': 'Error/Running'}
            data_dict.update(get_opt_points(gauf))
            data_dict.update(get_converge(gauf))

        data_list.append(data_dict)

    # merge data into a big dict
    data_df = pd.DataFrame(data_list)

    # use goodvibes
    if need_goodvibes:
        print('Running goodvibes!')
        p = subprocess.Popen(f'python -m goodvibes -c 1 -t {temp} *', shell=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.wait()
        gv_df = extract_goodvibes_result()
        if gv_df.empty:
            print('No valid goodvibes results!')
            need_goodvibes = False
        else:
            print('Merging goodvibes and gaussian results!')
        data_df = merge_and_update(data_df, gv_df)
    
    # run solvent correction with both goodvibes and entropy terms
    if need_entropy and need_goodvibes:
        print('Calculating entropy correction in solvent model!')
        data_df = get_solv_corr(data_df, temp)

    # write data into csv
    output_file = 'gauprocess.csv'
    data_df.to_csv(output_file, index=False)
    print('All data wrote to gauprocess.csv in current folder!')


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--entropy', '-s',
        action='store_const',
        const=True,
        default=False,
        help='if specified, extract output different entropy terms in gaussian output file (default: False)',
    )
    p.add_argument(
        '--goodvibes', '-g',
        action='store_const',
        const=True,
        default=False,
        help='if specified, run goodvibes and merge the results with original gaussian output (default: False)',
    )
    p.add_argument(
        '--temperature', '-t',
        type=float,
        default=298.15,
        help='temperature used in free energy calculation (default: 298.15K)',
    )
    return p.parse_args()

