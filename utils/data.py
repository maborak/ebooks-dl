from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm.db import BooksTable
from orm.db import Base

schema_url = 'mysql+mysqlconnector://root:adalidcampeon@192.168.0.250:3306/letmeread'
# schema_url = 'sqlite:///db.sqlite'
engine = create_engine(schema_url, echo=False)
Base.metadata.create_all(engine)


class DataEngine():
    session: object = None

    def __init__(self, orm: str = ''):
        Session = sessionmaker(bind=engine)
        self.session = Session()

    @staticmethod
    def drop_all():
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def save(self, book_data: list = []) -> bool:
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
            description=book_data['description']
        )
        self.session.add(c1)
        result = self.session.commit()
        return result

    def isset_code(self, code: str = '') -> bool:
        isset = self.session.query(BooksTable.id).filter(BooksTable.code == code)
        r = False if isset.first() is None else True
        return r

    def get_engine(self):
        return self.session, BooksTable