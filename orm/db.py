from sqlalchemy import Column, Integer, String, Text, Date, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
db_metadata = MetaData()


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
    engine = Column(String(255))
    format = Column(String(255), default="text")
    size = Column(Integer(), default=0)


bt = Table('books', db_metadata,
           Column('id', Integer, primary_key=True),
           Column('title', String(255)),
           Column('date', Date()),
           Column('pages', Integer(), default=0),
           Column('language', String(255)),
           Column('code', String(255)),
           Column('url', String(255)),
           Column('author', String(255)),
           Column('publisher', String(255)),
           Column('isbn10', String(255)),
           Column('isbn13', String(255)),
           Column('thumbnail', String(255)),
           Column('description', Text()),
           Column('engine', String(255)),
           Column('format', String(255), default='text'),
           Column('size', Integer(), default=0)
           )
