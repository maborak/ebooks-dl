from sqlalchemy import Column, Integer, String, Text, Date, Table, MetaData, Float, Sequence, NVARCHAR
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
db_metadata = MetaData()


class BooksTable(Base):
    __tablename__ = 'books'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci'
    }

    #uid = Column(Integer(), Sequence('uid_seq'), primary_key=True)
    uid = Column(Integer(), autoincrement=True, primary_key=True)
    #title = Column(String(355, convert_unicode=True, collation="utf8mb4_general_ci"))
    title = Column(String(355, convert_unicode=True))
    date_published = Column(Date(), nullable=True)
    date_posted = Column(Date(), nullable=True)
    pages = Column(Integer(), default=0)
    language = Column(String(255))
    duration = Column(Integer())
    duration_literal = Column(String(255))
    thumbnail = Column(String(255))
    code = Column(String(255))
    url = Column(String(255))
    author = Column(String(1255))
    publisher = Column(String(255))
    isbn10 = Column(String(255))
    isbn13 = Column(String(255))
    description = Column(Text)
    engine = Column(String(255))
    format = Column(String(255), default="text")
    size = Column(Integer(), default=0)
    size_literal = Column(String(255))
    rating = Column(Float(), default=0.0)
    link_status = Column(String(255), default='up')


bt = Table('books', db_metadata,
           Column('uid', Integer(), primary_key=True),
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
           Column('size', Integer(), default=0),
           Column('rating', Float(), default=0.0)
           )
