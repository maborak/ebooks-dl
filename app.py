from engines import letmeread
from utils import data
from utils.number import chunkit
import argparse
from utils.threads import Concurrent
from utils.data import DataEngine

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
    if args.drop_all is True:
        de = data.DataEngine(orm=args.orm)
        de.drop_all()

    if args.threads > 0:
        lr = letmeread.Engine(orm=args.orm)
        nop = lr.num_of_pages_to_process(start_from_page=args.start_from_page)
        print(nop)
        print("--------------")
        pools = chunkit(nop, args.threads)
        del lr
        engine = {
            'class': letmeread.Engine,
            'args': {
                'orm': args.orm
            }
        }
        c = Concurrent()
        c.schedule(tasks=pools, engine=engine, handler=DataEngine.concurrent_handler)
        print(33)
        exit()
    elif args.fix is True:
        a.fix()
    else:
        a.run(start_from_page=args.start_from_page, threads=args.threads, drop_all=args.drop_all)
