# extract data from gaussian output files and goodvibe output files
# Author: Zihao Ye & Alexander J Maertens
# creation time: Dec, 2022
# version: 2025/02/15

import os
import re
import sys
from copy import copy
from typing import List

import pandas as pd

# template to get single point energy
PATTERN_LIST = [
    r'CCSD\(T\)=(-?\d+\.\d+)(\\|\|)R',
    r'MP2=(-?\d+\.\d+)(\\|\|)R',
    r'HF=(-?\d+\.\d+)(\\|\|)R',
    r'CCSD\(T\)=(-?\d+\.\d+)(\\|\|)S',
    r'MP2=(-?\d+\.\d+)(\\|\|)S',
    r'HF=(-?\d+\.\d+)(\\|\|)S',
]


def get_status(gauf):
    '''
    judge whether the job has terminated normally
    '''
    is_normal = 0 
    try:
        for i in range(1,10):
            if 'Normal termination' in gauf[-i]:
                is_normal = 1
                break
    except:
        is_normal = 0

    return is_normal


def get_imag_freq(gauf):
    '''
    get number of imaginary freqencies if avaliable.
    if no freq info, return -1
    '''
    try:
        num_imag = 0
        num_real = 0
        freq_cons = 0.0
        for line in gauf:
            if line.strip().startswith('Frequencies --'):
                freqs = line.split()[2:]
                for fr in freqs:
                    if float(fr) < 0.0:
                        num_imag += 1
                        if float(fr) < freq_cons:
                            freq_cons = float(fr)
                    elif float(fr) > 0.0:
                        num_real += 1
                        if freq_cons == 0.0:
                            freq_cons = float(fr)
                if num_real:
                    break
    except:
        num_imag = -1
        freq_cons = 0.0
    
    if num_imag == 0 and num_real == 0:
        num_imag = -1
        freq_cons = 0.0
    
    return {'num_imag': int(num_imag), 'freq_cons': round(freq_cons, 2)}


def get_sp_energy(gauf: List[str]):
    '''
    get single point energy data in gaussian output file
    if error occurs, return -1.0
    '''
    gauf = [x.strip() for x in gauf]
    gauf = ''.join(gauf)
    gauf = gauf.replace('\n', '')

    for pattern in PATTERN_LIST:
        match = re.search(pattern, gauf)
        if match:
            try:
                sp_energy = round(float(match.group(1)), 6)
                break
            except ValueError:
                sp_energy = -1.0
        else:
            sp_energy = -1.0

    return {'E': sp_energy}


def get_free_energy(gauf):
    '''
    get free energy data in gaussian output file
    if error occurs, return -1.0
    '''
    free_corr = 0.0
    free_energy = 0.0
    try:
        for i in range(len(gauf)):
            if 'Thermal correction to Gibbs Free Energy=' in gauf[i]:
                free_corr = gauf[i].split()[-1]
            if 'Sum of electronic and thermal Free Energies=' in gauf[i]:
                free_energy = gauf[i].split()[-1]

        free_corr = round(float(free_corr), 6)
        free_energy = round(float(free_energy), 6)
    except:
        free_corr = -1.0
        free_energy = -1.0

    return {'G_corr': free_corr, 'G': free_energy}


def get_opt_points(gauf):
    '''
    get how many optimization points are there in the output file
    by searching for Step number * in the file
    '''
    rev_gauf = copy(gauf)
    rev_gauf.reverse() # search from the bottom

    opt_points = 0
    try:
        for i in range(len(rev_gauf)):
            
            if 'Step number' in rev_gauf[i]:
                opt_points = rev_gauf[i].split()[2]
                break
        opt_points = int(opt_points)
    except:
        opt_points = -1
    
    return {'opt_points': int(opt_points)}


def get_converge(gauf):
    '''
    get converge status for optimization jobs
    number refers to how many 'yes' are there in the last step
    '''
    rev_gauf = copy(gauf)
    rev_gauf.reverse() # search from the bottom

    converge = 0
    try:
        for i in range(len(rev_gauf)):
            if 'Converged?' in rev_gauf[i]:
                for j in range(1,5):
                    if rev_gauf[i-j].split()[-1] == 'YES':
                        converge += 1
                break
    except:
        converge = -1

    return {'converge': int(converge)}


def get_entropy(gauf):
    '''
    get different (rot, trans, vib, total) entropies from freq calculation
    useful when doing correction for implicit solvent model
    '''
    tot_S = -1.0
    elec_S = -1.0
    trans_S = -1.0
    rot_S = -1.0
    vib_S = -1.0

    for i in range(len(gauf)):
        if 'Sum of electronic and thermal Free Energies=' in gauf[i]:
            idx = i + 4
            tot_S = round(float(gauf[idx].split()[-1]), 3)
            elec_S = round(float(gauf[idx+1].split()[-1]), 3)
            trans_S = round(float(gauf[idx+2].split()[-1]), 3)
            rot_S = round(float(gauf[idx+3].split()[-1]), 3)
            vib_S = round(float(gauf[idx+4].split()[-1]), 3)
            break

    return {'S_tot': tot_S, 'S_elec': elec_S, 
            'S_trans': trans_S, 'S_rot': rot_S, 'S_vib': vib_S}


def extract_goodvibes_result(gv_file='Goodvibes_output.dat'):
    '''extract results from goodvibes outputfile'''
    with open(gv_file, 'r') as g:
        glines = g.readlines()
    
    idx_list = []
    for i, line in enumerate(glines):
        if line.strip().startswith('*****'):
            idx_list.append(i)
    
    if len(idx_list) == 2:
        start_idx = idx_list[0]
        end_idx = idx_list[1]

        data_list = []
        for i in range(start_idx + 1, end_idx):
            line = glines[i].strip()
            if line.startswith('o'):
                s_line = line.split()
                data_dict = {'file_name': s_line[1],
                             'ZPE': round(float(s_line[3]), 6),
                             'H_corr': round(float(s_line[4]) - float(s_line[2]), 6),
                             'H': round(float(s_line[4]), 6),
                             'T.qh-S_tot': round(float(s_line[6]), 6),
                             'qh-G_corr': round(float(s_line[8]) - float(s_line[2]), 6),
                             'qh-G': round(float(s_line[8]), 6),
                             }
                data_list.append(data_dict)
        
        gv_df = pd.DataFrame(data_list)
        return gv_df
    else:
        return pd.DataFrame([])


def get_solv_corr(data_df, temp, factors):
    '''calculate corrected free energy based on both goodvibes result and entropy scaling'''
    def compute_corr(row, temp, factors):
        # check both entropy and goodvibes output exist
        if row['H_corr'] and row['T.qh-S_tot'] and row['S_tot']:
            # compute the solv-G_corr with 50% scaling for S_rot and S_trans
            corr = round(row['H_corr'] -
                            (row['T.qh-S_tot'] -
                                ((1-factors[0]) * temp * row['S_rot'] +
                                 (1-factors[1]) * temp * row['S_trans'])
                                 / 1000 / 627.509
                             ),
                         6)
        else:
            corr = None
        return corr

    data_df['solv-G_corr'] = data_df.apply(compute_corr, args=(temp, factors), axis=1)

    def compute_corrected_G(row):
        # check both G_corr and electron energy output exist
        if row['solv-G_corr'] and row['E']:
            corr_G = round(row['E'] + row['solv-G_corr'], 6)
        else:
            corr_G = None
        return corr_G

    data_df['solv-G'] = data_df.apply(compute_corrected_G, axis=1)
    
    return data_df
