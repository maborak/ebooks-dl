import re
from datetime import datetime
from bs4 import BeautifulSoup
from utils.http import wget
from utils.data import DataEngine
from pprint import pprint as pp
from dateutil import parser


class Engine(object):
    """
    Engine to process: http://www.allitebooks.org/
    """
    __host__ = 'allitebooks'
    baseurl: str = "http://www.allitebooks.org/"
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

    def process_item(self, code: str, referer: str = '', url: str = None) -> object:
        if url is None:
            return False
        item_url = url
        bs = BeautifulSoup(wget(item_url, referer=referer), 'html.parser')
        try:
            title = bs.find("h1", {'class': 'single-title'}).get_text()
            try:
                sub = bs.find("header", {'class': 'entry-header'}).find("h4").get_text().strip()
                sub = ": " + sub
            except Exception:
                sub = ""
            title = f"{title}{sub}"
        except Exception:
            title = 'none'
        try:
            du = re.search("/uploads/([0-9]+)/([0-9]+)/", bs.find("img", {'class': 'attachment-post-thumbnail'})['src'].strip())
            date_posted = datetime.strptime(f"{du[1]}-{du[2]}", "%Y-%m").date()
        except Exception:
            date_posted = None
        try:
            thumb = bs.find("img", {'class': 'attachment-post-thumbnail'})['src'].strip()
        except Exception:
            thumb = 'none'
        try:
            description = bs.find("div", "entry-content")
            description.find("h3").decompose()
        except Exception:
            description = 'none'
        submetadata = bs.find("div", {'class': 'book-detail'}).findAll("dd")
        #pp(submetadata)
        #exit()
        try:
            mdate = submetadata[2].get_text().strip()
            date_published = datetime.strptime(mdate, '%Y').date()
        except Exception:
            date_published = None
        try:
            author = submetadata[0].get_text().strip()
        except Exception:
            author = None
        try:
            publisher = None
        except Exception:
            publisher = None
        try:
            pages = submetadata[3].get_text().strip()
        except Exception:
            pages = 0
        try:
            language = submetadata[4].get_text().strip()
        except Exception:
            language = None
        s = submetadata[5].get_text().strip()
        try:
            s = submetadata[5].get_text().strip()
            size = int(round(float(re.search("(.*) MB", s)[1]))) * 1024 * 1024
            size_literal = s
        except Exception:
            size = 0
            size_literal = None
        try:
            isbn = submetadata[1].get_text().strip().replace("-", "").split(",")[0]
            isbn13 = f"978{isbn}" if len(isbn) < 13 else isbn
            isbn10 = isbn
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
        return data

    def process_page(self, page_number: int = 1, progressbar: object = None) -> []:
        #print("Processing Page: " + str(page_number) + " of " + str(self.total_of_pages))
        page_url = f"{self.baseurl}/page/{page_number}/" if page_number > 1 else self.baseurl
        bs = BeautifulSoup(wget(page_url), 'html.parser')
        nameList = bs.find("div", {'class': 'main-content-inner'}).findAll("article", {'class': 'post'})
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
        bs = BeautifulSoup(wget(self.baseurl), 'html.parser')
        content = bs.find("div", {'class': 'main-content-inner'}).findAll("article")
        total_pages = int(bs.find("div", {'class': 'pagination'}).findAll("a")[-1].get_text())
        self.total_of_pages = total_pages
        self.total_items_per_page = len(content)
        return total_pages, self.total_items_per_page

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
