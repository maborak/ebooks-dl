from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm.db import BooksTable
from orm.db import Base

engine = create_engine(
    'mysql+mysqlconnector://root:adalidcampeon@192.168.0.250:3306/letmeread', echo=False)

#Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


class Data():
    @classmethod
    def save(book_data: list = []) -> bool:
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
            isbn13=book_data['isbn13']
        )
        session.add(c1)
        result = session.commit()
        return result

    def isset_code(self, code: str = '') -> bool:
        isset = session.query(BooksTable.id).filter(BooksTable.code == code)
        return False if isset.first() is None else True


db = Data()
