# process gaussian output file
# Author: Zihao Ye
# creation time: Dec, 2022
# version: 2025/02/01

import os
import re
import sys
from copy import copy
from typing import List

# template to get single point energy
PATTERN_LIST = [
    r'CCSD\(T\)=(-?\d+\.\d+)(\\|\|)R',
    r'MP2=(-?\d+\.\d+)(\\|\|)R',
    r'HF=(-?\d+\.\d+)(\\|\|)R'
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
    
    return {'num_imag': num_imag, 'freq_cons': freq_cons}


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
                sp_energy = float(match.group(1))
                break
            except ValueError:
                sp_energy = -1.0
        else:
            s_penergy = -1.0
    return {'sp_energy': sp_energy}


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

        free_corr = float(free_corr)
        free_energy = float(free_energy)
    except:
        free_corr = -1.0
        free_energy = -1.0

    return {'free_corr': free_corr, 'free_energy': free_energy}


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
    
    return {'opt_points': opt_points}


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

    return {'converge': converge}


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
            tot_S = float(gauf[idx].split()[-1])
            elec_S = float(gauf[idx+1].split()[-1])
            trans_S = float(gauf[idx+2].split()[-1])
            rot_S = float(gauf[idx+3].split()[-1])
            vib_S = float(gauf[idx+4].split()[-1])
            break

    return {'tot_S': tot_S, 'elec_S': elec_S, 
        'trans_S': trans_S, 'rot_S': rot_S, 'vib_S': vib_S}

