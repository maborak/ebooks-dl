import re
from datetime import datetime
from bs4 import BeautifulSoup
from utils.http import wget
from utils.data import DataEngine
from pprint import pprint as pp

class Engine(object):
    """
    Engine to process: https://coderprog.com/
    """
    __host__ = 'coderprog'
    baseurl: str = "https://coderprog.com"
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

    def process_item(self, code: str, referer: str = '') -> object:
        item_url = self.baseurl + "/" + code + "/"
        #item_url = "https://coderprog.com/red-hat-certified-engineer-rhel-8-rhce/"
        bs = BeautifulSoup(wget(item_url, referer=referer), 'html.parser')
        try:
            thumb = self.baseurl + bs.find("div", {'class': 'thecontent'}).find("img")['src']    
        except Exception:
            thumb = 'none'
        try:
            description = 'none'
        except Exception:
            description = 'none'
        try:
            title = bs.find("div", {'class': 'thecontent'}).find("img")['alt']    
        except Exception:
            title = 'none'
        metadata = bs.find("div", {'class': 'thecontent'}).findAll("div")[0].get_text().strip().split("\n")[1]
        submetadata = metadata.split("|")
        video = True if "MP4" in metadata else False
        if video is True:
            date = None
            pages = 0
            try:
                language = submetadata[0].strip()
            except Exception:
                language = 0
            try:
                size = 0
                size_literal = submetadata[-1].strip()
            except Exception:
                size = 0
                size_literal = None
            try:
                duration = 0
                duration_literal = submetadata[-2].strip()
            except Exception:
                duration = None
                duration_literal = None
            isbn10 = isbn13 = 0

        else:
            try:
                mdate = submetadata[1].strip()
                date = datetime.strptime(mdate, '%Y').date()
            except Exception:
                date = None
            try:
                pages = submetadata[3].strip()
                pages = re.search("([0-9]+) Pages", pages)[1]
            except Exception:
                pages = 0
            try:
                language = submetadata[0].strip()
            except Exception:
                language = 0
            try:
                s = submetadata[5].strip()
                size = int(re.search("([0-9]+) MB", s)[1]) * 1024 * 1024
                size_literal = s
            except Exception:
                size = 0
                size_literal = None
            try:
                isbn = submetadata[2].strip()
                ib = re.search("ISBN: ([0-9]+)", isbn)[1]
                isbn13 = "978-" + ib
                isbn10 = ib
            except Exception:
                isbn13 = 0
                isbn10 = 0
            duration_literal = duration = None
        data = {
            'title': title,
            'date': date,
            'pages': pages,
            'language': language,
            'code': code,
            'url': item_url,
            'author': "none",
            'publisher': "none",
            'isbn10': isbn10,
            'isbn13': isbn13,
            'thumbnail': thumb,
            'engine': self.__host__,
            'format': 'text' if video is False else "video",
            'size': size,
            'size_literal': size_literal,
            'duration': duration,
            'duration_literal': duration_literal, 
            'description': str(description)
        }
        return data

    def process_page(self, page_number: int = 1, progressbar: object = None) -> []:
        #print("Processing Page: " + str(page_number) + " of " + str(self.total_of_pages))
        page_url = self.baseurl + "/page/" + str(page_number) + "/" if page_number > 1 else self.baseurl
        bs = BeautifulSoup(wget(page_url), 'html.parser')
        nameList = bs.find("div", {'id': 'content_box'}).findAll('article', {'class': 'latestPost'})
        data = []
        for _index, i in enumerate(nameList):
            if progressbar is not None:
                progressbar()
            
            data = i.find('h2').find('a')
            data_text = data.get_text()
            code = data['href'].replace(self.baseurl, "").replace("/", "")
            #print(f"\t\t[page={page_number}]item: " + str(index + 1) + " of " + str(len(nameList)))
            isset = self.data_engine.isset_code(code=code, engine=self.__host__)
            if isset is False:
                try:
                    book_data = self.process_item(code=code, referer=page_url)
                    self.item_save(book_data=book_data)
                    pass
                except Exception as e:
                    print(f"Error processing page: {page_url} , title: {data_text}, item: " + self.baseurl + "/" + code + "/")
                    print(e)
        return True

    def count_total_pages(self) -> int:
        bs = BeautifulSoup(wget(self.baseurl), 'html.parser')
        content = bs.findAll("a", {'class': 'page-numbers'})
        total_pages = int(content[-2].get_text().strip().replace(",", ""))
        
        total_items = bs.find("div", {'id': 'content_box'}).findAll('article', {'class': 'latestPost'})
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
            session.query(table).filter(table.id == i.id).update({table.date: processed['date']}, synchronize_session = False)
            pp.pprint((processed['url'], ": ", processed['date']))
            print("------------------ end -----------------------")
            session.commit()
