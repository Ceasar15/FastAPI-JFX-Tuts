import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from core.database.database import engine

Base = declarative_base()
metadata = Base.metadata


class Book(Base):
    __tablename__ = "book"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String)
    author = sa.Column(sa.String)
    price = sa.Column(sa.String)
    description = sa.Column(sa.String)
    time_created = sa.Column(sa.DateTime(
        timezone=True), server_default=func.now())

    def __repr__(self):
        return "title: {}, by author: {}".format(self.title, self.author)

Base.metadata.create_all(engine, Base.metadata.tables.values(),checkfirst=True)