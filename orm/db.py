from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class BooksTable(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    date = Column(Date())
    pages = Column(Integer())
    language = Column(String(255))
    code = Column(String(255))
    url = Column(String(255))
    author = Column(String(255))
    publisher = Column(String(255))
    isbn10 = Column(String(255))
    isbn13 = Column(String(255))
    thumbnail = Column(String(255))
    description = Column(Text)
