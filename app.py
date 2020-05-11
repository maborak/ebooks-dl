from engines import letmeread
from engines import coderprog
from utils import data
from utils.number import chunkit
import argparse
from utils.threads import Concurrent
from utils.data import DataEngine
from alive_progress import alive_bar

parser = argparse.ArgumentParser()
parser.add_argument('--start-from-page', action="store", type=int, default=1)
parser.add_argument('--threads', action="store", type=int, default=0)
parser.add_argument('--drop-all', action="store_true", default=False)
parser.add_argument('--fix', action="store_true", default=False)
parser.add_argument('--orm', action="store", type=str, default="sqlite:///books.sqlite3")
parser.add_argument('--search', action="store", type=str, default=None)
parser.add_argument('--limit', action="store", type=int, default=10)
parser.add_argument('--engine', action="store", type=str, default='letmeread')

args, _ = parser.parse_known_args()
if args.engine == 'letmeread':
    engine = letmeread
elif args.engine == 'coderprog':
    engine = coderprog
else:
    print("Aborting. Invalid engine")
    exit()

if args.search is not None:
    de = data.DataEngine(orm=args.orm)
    de.search(criteria=args.search, limit=args.limit)
else:
    if args.drop_all is True:
        de = data.DataEngine(orm=args.orm)
        de.drop_all()

    if args.threads > 0:
        lr = engine.Engine(orm=args.orm)
        nop, items_per_page = lr.num_of_pages_to_process(start_from_page=args.start_from_page)
        #print(nop)
        #print("--------------")
        pools = chunkit(nop, args.threads)
        del lr
        total_predicted_items = len(nop) * items_per_page
        #bar = Bar('Another Thread', max=total_predicted_items)
        with alive_bar(total_predicted_items, bar='blocks') as bar:
            engine = {
                'class': engine.Engine,
                'progressbar': lambda: bar("Processing threads"),
                'args': {
                    'orm': args.orm
                }
            }
            c = Concurrent()
            c.schedule(tasks=pools, engine=engine, handler=DataEngine.concurrent_handler)
            #bar.finish()
    elif args.fix is True:
        a = engine.Engine(orm=args.orm)
        a.fix()
    else:
        lr = engine.Engine(orm=args.orm)
        nop, items_per_page = lr.num_of_pages_to_process(start_from_page=args.start_from_page)
        total_predicted_items = len(nop) * items_per_page
        #bar = Bar('Processing: ', max=total_predicted_items)
        with alive_bar(total_predicted_items) as bar:
            for page in nop:
                lr.process_page(page_number=page, progressbar=lambda: bar("Processing..."))
