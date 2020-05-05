from engines import letmeread
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--start-from-page', action="store", type=int, default=1)
parser.add_argument('--threads', action="store", type=int, default=0)
parser.add_argument('--drop-all', action="store_true", default=False)
parser.add_argument('--fix', action="store_true", default=False)
parser.add_argument('--orm', action="store", type=str, default="sqlite:///db.sqlite")


args, _ = parser.parse_known_args()
a = letmeread.Engine()
if args.fix is True:
    a.fix()
else:
    a.run(start_from_page=args.start_from_page, threads=args.threads, drop_all=args.drop_all)
