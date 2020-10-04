import re
from datetime import datetime
from bs4 import BeautifulSoup
from ..utils.http import wget
from ..utils.data import DataEngine
from dateutil import parser, tz


class Engine(object):
    """
    Engine to process: https://www.letmeread.net
    """
    __host__ = 'letmeread'
    baseurl: str = "https://www.letmeread.net"
    total_of_pages: int = 0
    total_of_pages_classified: int = 0
    orm: str = ''
    data_engine: str = object

    def __init__(self, orm: str = '', **kwargs) -> None:
        self.orm = orm
        self.data_engine = DataEngine(orm=self.orm)

    def item_save(self, book_data: list) -> bool:
        try:
            result = self.data_engine.save(book_data)
        except Exception:
            result = False
        return result

    def process_item(self, code: str) -> object:
        item_url = self.baseurl + "/" + code + "/"
        bs = BeautifulSoup(wget(item_url), 'html.parser')
        try:
            du = bs.find("meta", {'property': 'article:published_time'})['content']
            date_posted = parser.parse(du).date()
        except Exception:
            date_posted = None
        try:
            thumb = bs.find("img", {'class': 'align-self-start img-fluid'})['src']
        except Exception:
            thumb = 'none'
        try:
            description = bs.find("div", {'class': 'col-md-8'}).find("div", {'class': 'card mb-4'}).find("div", {'class':'card-body'})
        except Exception:
            description = 'none'
        data = {
            'title': "none",
            'date_published': None,
            'date_posted': date_posted,
            'pages': 0,
            'language': "none",
            'code': code,
            'url': item_url,
            'author': "none",
            'publisher': "none",
            'isbn10': "",
            'isbn13': "none",
            'thumbnail': thumb,
            'engine': 'letmeread',
            'format': 'text',
            'size': 0,
            'description': (description)
        }
        c = bs.find("ul", {'class': 'list-unstyled mb-0'}).findAll("li")
        for i in c:
            cc = i.get_text().strip()
            item = re.findall("([a-zA-Z0-9\- ]+): (.*)", cc)
            # print(item)
            ititle = item[0][0].strip()
            ivalue = item[0][1].strip()
            if(ititle == "Title"):
                data['title'] = ivalue
            elif(ititle == "Author"):
                data['author'] = ivalue
            elif(ititle == "Length"):
                num_of_pages = re.search("([0-9]+) pages", ivalue)[1]
                data['pages'] = num_of_pages
            elif(ititle == "Language"):
                data['language'] = ivalue
            elif(ititle == "Publisher"):
                data['publisher'] = ivalue
            elif(ititle == "Publication Date"):
                try:
                    d = datetime.strptime(ivalue, '%Y').date()
                    data['date_published'] = d
                except Exception:
                    try:
                        d = datetime.strptime(ivalue, '%Y-%m-%d').date()
                        data['date_published'] = d
                    except Exception:
                        try:
                            d = datetime.strptime(ivalue, '%Y-%m').date()
                            data['date_published'] = d
                        except Exception:
                            pass
            elif(ititle == "ISBN-10"):
                data['isbn10'] = ivalue
            elif(ititle == "ISBN-13"):
                data['isbn13'] = ivalue
        return data

    def process_page(self, page_number: int = 1, progressbar: object = None) -> []:
        #print("Processing Page: " + str(page_number) + " of " + str(self.total_of_pages))
        page_url = self.baseurl + "/page/" + str(page_number) + "/" if page_number > 1 else self.baseurl
        bs = BeautifulSoup(wget(page_url), 'html.parser')
        nameList = bs.findAll('div', {'class': 'card-body p-2'})
        data = []
        for _index, i in enumerate(nameList):
            if progressbar is not None:
                progressbar()
            data = i.find('a')
            data_text = data.get_text()
            code = data['href'].replace("/", "")
            #print(f"\t\t[page={page_number}]item: " + str(index + 1) + " of " + str(len(nameList)))
            isset = self.data_engine.isset_code(code=code, engine=self.__host__)
            if isset is False:
                try:
                    book_data = self.process_item(code=code)
                    self.item_save(book_data=book_data)
                    pass
                except Exception as e:
                    print(f"Error processing page: {page_url} , title: {data_text}, item: " + self.baseurl + "/" + code + "/")
                    print(e)
        return True

    def count_total_pages(self) -> int:
        bs = BeautifulSoup(wget(self.baseurl), 'html.parser')
        content = bs.find(
            "li", {'class': 'page-item disabled d-none d-lg-block'})
        sp = re.search(
            'of ([0-9]+)', content.get_text().strip(), flags=re.IGNORECASE)
        total_pages = int(sp[1])
        total_items = bs.findAll('div', {'class': 'card-body p-2'})
        self.total_of_pages = total_pages
        self.totat_items_per_page = len(total_items)
        return total_pages, self.totat_items_per_page

    def num_of_pages_to_process(self, start_from_page: int = 1) -> ([], int):
        """
        Return all the sanitized pages

        Keyword Arguments:
            start_from_page {int} -- What page are going to start (default: {1})

        Returns:
            list -- All the pages to be processed
        """
        total_pages, num_items_per_page = self.count_total_pages()
        entries = []
        for i in range(total_pages):
            current_page = i + 1
            if current_page >= start_from_page:
                entries.append(i + 1)
        self.total_of_pages_classified = len(entries)
        return entries, num_items_per_page

    def run(self, start_from_page: int = 1) -> None:
        pages, _ = self.num_of_pages_to_process(start_from_page=start_from_page)
        for current_page in pages:
            self.process_page(current_page)

    def fix(self):
        import pprint as pp
        d = DataEngine()
        session, table = d.get_engine()
        r = session.query(table).filter(table.date == "0000-00-00").all()
        for i in r:
            processed = self.process_item(i.code)
            print("------------------ begin ----------------------")
            #table.__table__.update().where(table.id==i.id).values(date=processed['date'])
            session.query(table).filter(table.uid == i.uid).update({table.date_published: processed['date_published']}, synchronize_session = False)
            pp.pprint((processed['url'], ": ", processed['date']))
            print("------------------ end -----------------------")
            session.commit()
