import re
from datetime import datetime
from bs4 import BeautifulSoup
from utils.http import wget
from utils.data import db


class Engine(object):
    baseurl: str = "https://www.letmeread.net"
    total_of_pages: int = 0

    @classmethod
    def item_save(self, book_data: list) -> bool:
        result = db.save(book_data)
        return result

    @classmethod
    def process_item(self, code: str) -> object:
        item_url = self.baseurl + "/" + code + "/"
        bs = BeautifulSoup(wget(item_url), 'html.parser')
        c = bs.find("ul", {'class': 'list-unstyled mb-0'}).findAll("li")
        data = {
            'title': "none",
            'date': 0,
            'pages': 0,
            'language': "none",
            'code': code,
            'url': item_url,
            'author': "none",
            'publisher': "none",
            'isbn10': "",
            'isbn13': "none"
        }
        for i in c:
            cc = i.get_text().strip()
            item = re.findall("([a-zA-Z0-9\- ]+): (.*)", cc)
            print(item)
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
                    d = datetime.strptime(ivalue, '%Y')
                    data['date'] = str(d)
                except Exception:
                    try:
                        d = datetime.strptime(ivalue, '%Y-%m-%d')
                        data['date'] = str(d)
                    except Exception:
                        pass
            elif(ititle == "ISBN-10"):
                data['isbn10'] = ivalue
            elif(ititle == "ISBN-13"):
                data['isbn13'] = ivalue
        return data

    @classmethod
    def process_page(self, page_number: int = 1) -> []:
        print("Processing Page: " + str(page_number) +
              " of " + str(self.total_of_pages))
        page_url = self.baseurl + "/page/" + \
            str(page_number) + "/" if page_number > 1 else self.baseurl
        bs = BeautifulSoup(wget(page_url), 'html.parser')
        nameList = bs.findAll('div', {'class': 'card-body p-2'})
        data = []
        for index, i in enumerate(nameList):
            data = i.find('a')
            # title = data.get_text().strip()
            code = data['href'].replace("/", "")
            # url = self.baseurl + "/" + code + "/"
            print("\t\titem: " + str(index + 1) + " of " + str(len(nameList)))
            isset = db.isset_code(code)
            if isset is False:
                try:
                    book_data = self.process_item(code)
                    self.item_save(book_data)
                except Exception:
                    pass
        return data

    @classmethod
    def total_pages(self) -> int:
        bs = BeautifulSoup(wget(self.baseurl), 'html.parser')
        content = bs.find(
            "li", {'class': 'page-item disabled d-none d-lg-block'})
        sp = re.search(
            'of ([0-9]+)', content.get_text().strip(), flags=re.IGNORECASE)
        total_pages = int(sp[1])
        self.total_of_pages = total_pages
        return total_pages

    @classmethod
    def run(self):
        total_pages = self.total_pages()
        for i in range(total_pages):
            current_page = i + 1
            self.process_page(current_page)
