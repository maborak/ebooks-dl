from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from orm.db import BooksTable, bt, db_metadata
from orm.db import Base
import termtables as tt
import json


class DataEngine():
    session: object = None
    engine: object = None
    __default__orm: str = ''
    use_orm: bool = True
    db_metadata: object = None

    def __init__(self, orm: str = ''):
        self.__default__orm = self.__default__orm if not orm else orm
        self.engine = create_engine(self.__default__orm, echo=False)
        self.use_orm = True
        if self.use_orm is True:
            self.db_metadata = Base.metadata
            self.db_metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        else:
            self.db_metadata = db_metadata
            self.db_metadata.create_all(self.engine)

    def drop_all(self):
        self.db_metadata.drop_all(self.engine)
        self.db_metadata.create_all(self.engine)

    def save(self, book_data: list = []) -> bool:
        if self.use_orm is True:
            #ins = BooksTable().insert().values(title="pito")
            #return True
            c1 = BooksTable(
                title=book_data['title'],
                date=book_data['date'],
                pages=book_data['pages'],
                language=book_data['language'],
                code=book_data['code'],
                url=book_data['url'],
                author=book_data['author'],
                publisher=book_data['publisher'],
                isbn10=book_data['isbn10'],
                isbn13=book_data['isbn13'],
                thumbnail=book_data['thumbnail'],
                description=book_data['description'],
                engine=book_data['engine'],
                format=book_data['format'],
                size=book_data['size']
            )
            self.session.add(c1)
            result = self.session.commit()
        else:
            result = self.engine.execute(bt.insert().values([book_data]))
        return result

    def isset_code(self, code: str = '') -> bool:
        if self.use_orm is True:
            isset = self.session.query(BooksTable.id).filter(BooksTable.code == code)
            r = False if isset.first() is None else True
        else:
            s = select([bt.c.id]).where(bt.c.code == code)
            r = False if self.engine.execute(s).fetchone() is None else True
        return r

    def get_engine(self):
        return self.session, BooksTable

    def search(self, criteria: str = '', limit: int = 10, format: str = 'table'):
        r = self.session.query(BooksTable.title, BooksTable.date, BooksTable.url)\
                .filter(BooksTable.title.like(criteria))\
                .order_by(desc(BooksTable.date))\
                .limit(limit)
        data = []
        header = ['Date', 'Title', 'Url']
        for book in r:
            data.append([str(book.date), book.title, book.url])
        if format == 'table':
            if len(data) == 0:
                tt.print([[f"No results for: {criteria}"]], style=tt.styles.ascii_thin)
            else:    
                tt.print(data, header=header, padding=(0, 1), style=tt.styles.ascii_thin, alignment='lll')
        elif format == 'json':
            print(json.dumps(data))
        return data
