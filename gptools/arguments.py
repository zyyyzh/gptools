# get arguments for using gptools
# Author: Zihao Ye & Alexander J Maertens
# creation time: Dec, 2022
# version: 2025/06/16

import argparse


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--file', '-f',
        type=str,
        help='Specify a single file to process (must be .log or .out)',
    )
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
    p.add_argument(
        '--concentration', '-c',
        type=float,
        default=1.0,
        help='concentration used in free energy calculation (default: 1.0M)',
    )
    p.add_argument(
        '--factor_rot',
        type=float,
        default=0.5,
        help='scaling factor for S_rot (default: 0.5)',
    )
    p.add_argument(
        '--factor_trans',
        type=float,
        default=0.5,
        help='scaling factor for S_trans (default: 0.5)',
    )
    p.add_argument(
        '--gensi',
        action='store_const',
        const=True,
        default=False,
        help='if specified, generate .txt file for SI after processing (default: False)',
    )
    return p.parse_args()
