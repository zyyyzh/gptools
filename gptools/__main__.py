from gptools.gauprocess import (parse_args, process)


if __name__ == '__main__':
    args = parse_args()
    process(inp_file=args.file,
            need_entropy=args.entropy,
            need_goodvibes=args.goodvibes,
            temp=args.temperature,
            conc=args.concentration,
            factor_rot=args.factor_rot,
            factor_trans=args.factor_trans,
            )
