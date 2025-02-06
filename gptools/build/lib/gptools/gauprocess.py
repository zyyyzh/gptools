# collect and process gaussian output file
# Author: Zihao Ye
# creation time: Dec, 2022
# version: 2025/02/01

import os
import re
import sys
import csv
import argparse
from copy import copy

from gptools.extractors import [
    get_status,
    get_sp_energy,
    get_free_energy,
    get_imag_freq,
    get_entropy,
    get_opt_points,
    get_converge,
]
from gptools.utils import merge_dicts


def process(work_dir: str=os.getcwd(),
            need_entropy: bool=False,
            need_goodvibes: bool=False,
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
    for file in gau_list:
        gau_file = os.path.abspath(work_dir + '/' + file)
        with open(gau_file) as f:
            gauf = f.readlines()
        # normal termination
        if get_status(gauf): 
            data_dict = {'file_name': file, 'status': 'Normal'}
            data_dict.update(get_sp_energy(gauf))
            data_dict.update(get_free_energy(gauf))
            # has freq calculation
            if (data_dict['free_energy'] != 0.0) or (data_dict['free_energy'] != -1.0):
                data_dict.update(get_imag_freq(gauf))
                if need_entropy:
                    data_dict.update(get_entropy(gauf))
            # no freq calculation
            else:
                data_dict.update({'num_imag': -1, 'freq_cons': 0.0})
                if need_entropy:
                    data_dict.update({'tot_S': -1.0, 'elec_S': -1.0, 
                        'trans_S': -1.0, 'rot_S': -1.0, 'vib_S': -1.0})

            # out_list.append([file, 'Normol', '{:.7f}'.format(float(spenergy)),
            #  '{:.7f}'.format(float(free_correction)), '{:.7f}'.format(float(free_energy)),
            #  '{}'.format(num_imag), '{:.2f}'.format(freq_cons),
            #  '{:.3f}'.format(tot_S), '{:.3f}'.format(elec_S), '{:.3f}'.format(trans_S),
            #  '{:.3f}'.format(rot_S), '{:.3f}'.format(vib_S), ' ', ' '])
        else:  # abnormal termination or running
            data_dict = {'file_name': file, 'status': 'Error/Running'}
            data_dict.update(get_opt_points(gauf))
            data_dict.update(get_converge(gauf))

        data_list.append(data_dict)

    # merge data into a big dict
    merged_dict = merge_dicts(data_list)

    # use goodvibes
    if need_goodvibes:
        print('use goodvibes!')

    # write data into csv
    output_file = 'gauprocess.csv'
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # write keys
        headers = result.keys()
        writer.writerow(headers)
        
        # write values
        max_length = max(len(v) for v in result.values())
        
        for i in range(max_length):
            row = []
            for key in headers:
                # add empty string for missing values
                if i < len(result[key]):
                    row.append(result[key][i])
                else:
                    row.append('')
            writer.writerow(row)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--entropy', '-s',
        action='store_const',
        const=True,
        default=False,
        help='if output entropy info (default: False)',
    )
    p.add_argument(
        '--goodvibes', '-g',
        action='store_const',
        const=True,
        default=False,
        help='if use goodvibes (default: False)',
    )
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()

    process(
            need_entropy=args.entropy,
            need_goodvibes=args.goodvibes
            )
