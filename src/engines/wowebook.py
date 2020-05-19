import re
from datetime import datetime
from bs4 import BeautifulSoup
from utils.http import wget
from utils.data import DataEngine
from pprint import pprint as pp
from dateutil import parser


class Engine(object):
    """
    Engine to process: https://www.wowebook.org/
    """
    __host__ = 'wowebook'
    baseurl: str = "https://www.wowebook.org"
    total_of_pages: int = 0
    total_items_per_page: int = 0
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

    def process_item(self, code: str = None, referer: str = '', url: str = None) -> object:
        if url is None:
            return False
        item_url = url
        bs = BeautifulSoup(wget(item_url, referer=referer), 'html.parser')
        try:
            title = bs.find("h1", {'class': 'post-title'}).get_text()
        except Exception:
            title = 'none'
        try:
            du = bs.find("time", {'class': 'published'}).get_text()
            date_posted = parser.parse(du).date()
        except Exception:
            date_posted = None
        try:
            thumb = bs.find('div', {'class': 'entry-inner'}).find("img", {'class': 'size-full'})['src'].strip()
        except Exception:
            thumb = 'none'
        try:
            description = 'none'
        except Exception:
            description = 'none'
        
        try:
            submetadata = bs.find("div", {'class': 'entry-inner'}).find("ul").get_text()
        except Exception:
            submetadata = ""
        #print(submetadata)
        #s = re.search(r"ISBN-13:\s([0-9a-zA-Z\-]+)", submetadata)[1]
        #print(s)
        #exit()
        try:
            date_published = re.search(r"\s\(([0-9a-zA-Z,\s]+)\)", submetadata)[1]
            date_published = parser.parse(date_published).date()
        except Exception:
            date_published = None
        try:
            author = None
        except Exception:
            author = None
        try:
            publisher = None
        except Exception:
            publisher = None
        try:
            pages = int(re.search(r":\s([0-9]+) pages", submetadata)[1])
        except Exception:
            pages = 0
        try:
            language = re.search(r"Language:\s([a-zA-Z]+)", submetadata)[1]
        except Exception:
            language = None

        try:
            size = None
            size_literal = size
        except Exception:
            size = 0
            size_literal = None
        try:
            isbn13 = re.search(r"ISBN-13:\s([0-9a-zA-Z\-]+)", submetadata)[1]
            isbn10 = re.search(r"ISBN-10:\s([0-9a-zA-Z]+)", submetadata)[1]
        except Exception:
            isbn13 = 0
            isbn10 = 0
        duration_literal = duration = None
        data = {
            'title': title,
            'date_published': date_published,
            'date_posted': date_posted,
            'pages': pages,
            'language': language,
            'code': code,
            'url': item_url,
            'author': author,
            'publisher': publisher,
            'isbn10': isbn10,
            'isbn13': isbn13,
            'thumbnail': thumb,
            'engine': self.__host__,
            'format': 'text',
            'size': size,
            'size_literal': size_literal,
            'duration': duration,
            'duration_literal': duration_literal, 
            'description': str(description)
        }
        #pp(data)
        #exit()
        return data

    def process_page(self, page_number: int = 1, progressbar: object = None) -> []:
        #print("Processing Page: " + str(page_number) + " of " + str(self.total_of_pages))
        page_url = f"{self.baseurl}/page/{page_number}/" if page_number > 1 else self.baseurl
        bs = BeautifulSoup(wget(page_url), 'html.parser')
        nameList = bs.find("div", {'class': 'post-list-standard'}).findAll("article")
        data = []
        for _index, i in enumerate(nameList):
            if progressbar is not None:
                progressbar()
            data = i.find('h2').find('a')
            code = data['href'].replace(self.baseurl, "").replace("/", "")
            url = data['href']
            isset = self.data_engine.isset_code(code=code, engine=self.__host__)
            if isset is False:
                try:
                    book_data = self.process_item(code=code, referer=page_url, url=url)
                    self.item_save(book_data=book_data)
                    pass
                except Exception as e:
                    print(f"Error processing page: {page_url} , title: {data.get_text()}, item: " + url)
                    print(e)
        return True

    def count_total_pages(self) -> int:
        if self.total_of_pages > 0:
            return self.total_of_pages, self.total_items_per_page
        bs = BeautifulSoup(wget(self.baseurl), 'html.parser')
        content = bs.find("div", {'class': 'post-list-standard'}).findAll("article")
        self.total_of_pages = self.inner_total_pages()
        self.total_items_per_page = len(content)
        return self.total_of_pages, self.total_items_per_page

    def b(self, lista: list = []):
        tam = len(lista)
        if tam <= 1:
            return lista[0]
        mid = tam // 2
        r = self.check_pn(lista[mid])
        if r == 1:
            return self.b(lista[mid:])
        elif r == 2:
            return self.b(lista[:mid])
        return lista[mid]

    def check_pn(self, data: object = {}) -> int:
        p = data['page']
        uri = f"{self.baseurl}/page/{p}"
        print(f" Checking: {uri}")
        r = wget(url=uri, only_status=True)
        if r == 200:
            rb = wget(url=f"{self.baseurl}/page/{p+1}", only_status=True)
            if rb != 200:
                return 3
            else:
                return 1
        else:
            return 2
        return 3

    def inner_total_pages(self):
        return 1500 #Forced
        a = []
        e = 10000
        for i in range(e):
            a.append({'page': i + 1})
        r = self.b(a)
        return r['page']

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
            session.query(table).filter(table.id == i.id).update({table.date: processed['date']}, synchronize_session = False)
            pp.pprint((processed['url'], ": ", processed['date']))
            print("------------------ end -----------------------")
            session.commit()
