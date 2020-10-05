from .utils import data
import argparse
from .utils.number import chunkit
from .utils.threads import Concurrent
from .utils.data import DataEngine
from .utils.utils import get_engine
from alive_progress import alive_bar
from termcolor import colored
import itertools


parser = argparse.ArgumentParser()
parser.add_argument('--start-from-page', action="store", type=int, default=1)
parser.add_argument('--threads', action="store", type=int, default=0)
parser.add_argument('--drop-all', action="store_true", default=False)
parser.add_argument('--fix', action="store_true", default=False)
parser.add_argument('--orm', action="store", type=str, default="sqlite:///books.sqlite3")
parser.add_argument('--search', action="store", type=str, default=None)
parser.add_argument('--limit', action="store", type=int, default=10)
parser.add_argument('--engine', action="store", type=str, default='letmeread')
parser.add_argument('--process-item', action="store", type=str, default=None)


args, _ = parser.parse_known_args()
engine = get_engine(args.engine)


if args.search is not None:
    de = data.DataEngine(orm=args.orm)
    de.search(criteria=args.search, limit=args.limit)
elif args.process_item is not None:
    de = engine.Engine(orm=args.orm)
    print(de.process_item(url=args.process_item, code=None))
else:
    if args.drop_all is True:
        de = data.DataEngine(orm=args.orm)
        de.drop_all()

    print("+----------------------------------------------------------------------")
    print(f"|          Using ORM: {colored(args.orm, 'green')}")
    print(f"|             Engine: {colored(args.engine, 'yellow')}")
    print(f"|            Threads: {colored(args.threads, 'green')}")
    print(f"| Starting from page: {colored(args.start_from_page, 'green')}")
    print("+----------------------------------------------------------------------\n")

    if args.threads > 0:
        lr = engine.Engine(orm=args.orm)
        nop, items_per_page = lr.num_of_pages_to_process(start_from_page=args.start_from_page)
        #print(nop)
        #print("--------------")
        pools = chunkit(nop, args.threads)
        del lr
        total_predicted_items = len(nop) * items_per_page
        print(f"Total pages: {len(nop)}, Items per page: {items_per_page}")
        #bar = Bar('Another Thread', max=total_predicted_items)
        with alive_bar(total_predicted_items, bar='blocks', manual=True) as bar:
            _counter = itertools.count()
            bar(0., "Processing Threads...")
            engine = {
                'class': engine.Engine,
                'progressbar': lambda: bar(next(_counter) / total_predicted_items),
                'args': {
                    'orm': args.orm
                }
            }
            c = Concurrent()
            c.schedule(tasks=pools, engine=engine, handler=DataEngine.concurrent_handler)
            bar(1.)
    elif args.fix is True:
        a = engine.Engine(orm=args.orm)
        a.fix()
    else:
        lr = engine.Engine(orm=args.orm)
        nop, items_per_page = lr.num_of_pages_to_process(start_from_page=args.start_from_page)
        total_predicted_items = len(nop) * items_per_page
        print(f"Total pages: {len(nop)}, Items per page: {items_per_page}")
        with alive_bar(total_predicted_items, manual=True) as bar:
            _counter = itertools.count()
            bar(0., "Processing...")
            for _index, page in enumerate(nop, start=1):
                lr.process_page(page_number=page, progressbar=lambda: bar(next(_counter) / total_predicted_items))
            bar(1.)
