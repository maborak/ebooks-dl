from engines import letmeread
from utils import data
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--start-from-page', action="store", type=int, default=1)
parser.add_argument('--threads', action="store", type=int, default=0)
parser.add_argument('--drop-all', action="store_true", default=False)
parser.add_argument('--fix', action="store_true", default=False)
parser.add_argument('--orm', action="store", type=str, default="sqlite:///db.sqlite")
parser.add_argument('--search', action="store", type=str, default=None)
parser.add_argument('--limit', action="store", type=int, default=10)


args, _ = parser.parse_known_args()
a = letmeread.Engine(orm=args.orm)
if args.search is not None:
    de = data.DataEngine(orm=args.orm)
    de.search(criteria=args.search, limit=args.limit)
else:
    if args.fix is True:
        a.fix()
    else:
        a.run(start_from_page=args.start_from_page, threads=args.threads, drop_all=args.drop_all)
