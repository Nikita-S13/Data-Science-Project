import sqlalchemy
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer,String,DateTime,Float
from sqlalchemy.ext import declarative
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Review(Base):
    __tablename__ ='reviews'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    person = Column(String)
    product = Column(String)
    sentiment = Column(Float)
    sentiment_name = Column(String)
    uploader = Column(String,default='nikita sachan')
    created_on = Column(DateTime, default=datetime.now)

    def __str__(self):
        return self.filename

if __name__ == "__main__":
    engine = create_engine('sqlite:///db.sqlite3')
    Base.metadata.create_all(engine)