from gptools.gauprocess import (parse_args, process)


if __name__ == '__main__':
    args = parse_args()
    process(
            need_entropy=args.entropy,
            need_goodvibes=args.goodvibes,
            temp=args.temperature,
            )
