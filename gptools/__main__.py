# collect and process gaussian output file
# Author: Zihao Ye & Alexander J Maertens
# creation time: Dec, 2022
# version: 2025/06/16

from gptools.arguments import parse_args
from gptools.gauprocess import process


if __name__ == '__main__':
    args = parse_args()
    # normal gaussian file processing
    process(inp_file=args.file,
            need_entropy=args.entropy,
            need_goodvibes=args.goodvibes,
            temp=args.temperature,
            conc=args.concentration,
            factor_rot=args.factor_rot,
            factor_trans=args.factor_trans,
            )
    # generate SI file from the files processed
    if args.gensi:
        try:
            from gptools.gensi import gensi
        except ImportError:
            print('package gjftools is needed for this function!')

        gensi(need_entropy=args.entropy,
              need_goodvibes=args.goodvibes,
              )
