# collect and process gaussian output file
# Author: Zihao Ye
# creation time: Dec, 2022
# version: 2025/02/01

import os
import re
import sys
import csv
import time
import argparse
from copy import copy
from typing import List

# 
PATTERN_LIST = [
    r'CCSD\(T\)=(-?\d+\.\d+)(\\|\|)R',
    r'MP2=(-?\d+\.\d+)(\\|\|)R',
    r'HF=(-?\d+\.\d+)(\\|\|)R'
]

# bash command to get queue info
QUEUE_CMD = "qstat -u zye"


def get_termination(gauf):
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


def main(main_dir: str=os.getcwd(),
         clean: bool=False,
         need_fchk: bool=False,
         need_file47: bool=False,
         need_error: bool=False,
         deepclean: bool=False,
         all_yes: bool=False,
         ):
    '''
    process all log or out file in dir and its sub dir startswith numbers
    determine whether they are normal termination
    if normal termination,
        get single point energy (HF=)
        get gibbs free energy correction and free energy
    if running or error,
        get optimization points
        get converge status
    output to a csv file
    '''
    # check if deepclean is required
    if deepclean:
        if all_yes:
            pass
        else:
            need_deepclean = input('Do you want delete error files? (y/n)')
            if need_deepclean != 'y':
                print('Aborted! Exit now!')
                sys.exit()
            else:
                pass
    # make log dir, collect log file and get log_path
    os.chdir(main_dir)
    if os.path.exists('log'):
        if all_yes:
            os.system('rm -rf log')
        else:
            print('Warning: old log folder exists!')
            need_remove = input('Do you want delete old log? (y/n)')
            if need_remove == 'y':
                os.system('rm -rf log')
            else:
                os.system(f'mv log log_{int(time.time()*100)}')
    os.makedirs('log', exist_ok=True)

    if need_fchk:
        if os.path.exists('fchk'):
            if all_yes:
                os.system('rm -rf fchk')
            else:
                print('Warning: old fchk folder exists!')
                need_remove = input('Do you want delete old fchk? (y/n)')
                if need_remove == 'y':
                    os.system('rm -rf fchk')
                else:
                    os.system(f'mv fchk fchk_{int(time.time()*100)}')
        os.makedirs('fchk', exist_ok=True)
    if need_file47:
        if os.path.exists('file47'):
            if all_yes:
                os.system('rm -rf fchk')
            else:
                print('Warning: old file47 folder exists!')
                need_remove = input('Do you want delete old file47? (y/n)')
                if need_remove == 'y':
                    os.system('rm -rf file47')
                else:
                    os.system(f'mv file47 fchk_{int(time.time()*100)}')
        os.makedirs('file47', exist_ok=True)
    if need_error:
        os.makedirs('log/error', exist_ok=True)

    for f in os.listdir():  # direct get files
        if f.endswith('.log'):
            os.system(f'cp {f} log/')
        elif f.endswith('.fchk'):
            if need_fchk:
                os.system(f'cp {f} fchk/')
        elif f.endswith('.47'):
            if need_file47:
                os.system(f'cp {f} file47/')
    
    for dir in os.listdir():  # get files from directories
        if dir.isdigit():
            os.system(f'cp {dir}/*.log log/')
            if need_fchk:
                os.system(f'cp {dir}/*.fchk fchk/')
            if need_file47:
                os.system(f'cp {dir}/*.47 file47/')

    log_path = os.path.abspath('log')

    # read running jobs
    queue_log = os.path.abspath(log_path + '/queue.log')
    os.system(f'{QUEUE_CMD} > {queue_log}')
    with open(queue_log, 'r') as l:
        queue_lines = l.readlines()
    running_jobid = [line.split()[0] for line in queue_lines[1:]]
    os.system(f'rm -rf {queue_log}')

    # process log file
    gau_list = [file for file in os.listdir(log_path)
                if file.endswith('.log') or file.endswith('.out')]
    gau_list.sort()

    out_list = []
    remove_list = []
    for file in gau_list:
        gau_file = os.path.abspath(log_path + '/' + file)
        with open(gau_file) as f:
            gauf = f.readlines()

        if get_termination(gauf):  # normal termination
            pass
        else:  # abnormal termination or running
            # get jobid
            ofile_list = [of for of in os.listdir(main_dir) if of.startswith(f"{file.split('.')[0]}.o")]
            if not ofile_list:
                jobid = ''
            else:
                ofile = ofile_list[0]
                jobid = ofile.split('.o')[-1]
            # determine running or error
            if jobid in running_jobid:  # running
                print(f'file {file} is still running!')
            else:  # error
                print(f'file {file} did not terminate normally!')
                if need_error:
                    os.system(f'cp log/{file} log/error/')
                if deepclean:
                    remove_list.append((file, jobid))
    
    # clean up file and dirs
    if clean or deepclean:
        for log_file, jobid in remove_list:
            prefix = log_file.split('.')[0]
            print(f'{prefix} is now deleting...')
            os.system(f'rm -f {prefix}.log')
            os.system(f'rm -f {prefix}.gjf')
            os.system(f'rm -f {prefix}.o*')
            os.system(f'rm -f {prefix}.po*')
            os.system(f'rm -rf {jobid}')


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--clean', '-c',
        action='store_const',
        const=True,
        default=False,
        help='remove finished job files (default: False)',
    )
    p.add_argument(
        '--deepclean', '-d',
        action='store_const',
        const=True,
        default=False,
        help='remove finished job files and error job files (default: False)',
    )
    p.add_argument(
        '--fchk', '-k',
        action='store_const',
        const=True,
        default=False,
        help='get fchk files (default: False)',
    )
    p.add_argument(
        '--file47', '-s',
        action='store_const',
        const=True,
        default=False,
        help='get 47 files (default: False)',
    )
    p.add_argument(
        '--error', '-e',
        action='store_const',
        const=True,
        default=False,
        help='copy all error files to one single folder (default: False)',
    )
    p.add_argument(
        '--yes', '-y',
        action='store_const',
        const=True,
        default=False,
        help='input y for all confirmation (default: False)',
    )
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()

    main(clean=args.clean,
         need_fchk=args.fchk,
         need_file47=args.file47,
         need_error=args.error,
         deepclean=args.deepclean,
         all_yes=args.yes,
         )
