from datetime import datetime as dt
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    Table,
    DateTime,
)

from .mixins import WithUrl, WithId

Base = declarative_base()

tag_post = Table(
    'tag_post',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)
comment_post = Table(
    'comment_post',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('comment_id', Integer, ForeignKey('comment.id'))
)


class Post(Base, WithId, WithUrl):
    __tablename__ = 'post'
    title = Column(
        String(250), nullable=False, unique=False
    )
    first_picture_link = Column(
        String(255), nullable=True, unique=False
    )
    date_of_publishing = Column(
        DateTime, nullable=False
    )

    author_id = Column(
        Integer, ForeignKey('author.id'), nullable=True
    )

    author = relationship('Author', backref='posts')
    tags = relationship('Tag', secondary=tag_post, backref='posts')
    comments = relationship('Comment', secondary=comment_post, backref='posts')

    def __init__(self, **kwargs):
        self.date_of_publishing = dt.fromisoformat(kwargs['date_of_publishing'])


class Author(Base, WithId, WithUrl):
    __tablename__ = "author"
    name = Column(
        String(150), nullable=False
    )


class Tag(Base, WithId, WithUrl):
    __tablename__ = 'tag'
    name = Column(
        String(150), nullable=False
    )
    posts = relationship(Post, secondary=tag_post)


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("comment.id"), nullable=True)
    likes_count = Column(Integer)
    body = Column(String)
    created_at = Column(DateTime, nullable=False)
    hidden = Column(Boolean)
    deep = Column(Integer)
    author_id = Column(Integer, ForeignKey("author.id"))
    author = relationship("Author", backref="comments")
    time_now = Column(DateTime)
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship(Post, secondary=comment_post, backref="comments")

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.parent_id = kwargs["parent_id"]
        self.likes_count = kwargs["likes_count"]
        self.body = kwargs["body"]
        self.created_at = dt.fromisoformat(kwargs["created_at"])
        self.hidden = kwargs["hidden"]
        self.deep = kwargs["deep"]
        self.time_now = dt.fromisoformat(kwargs["time_now"])
        self.author = kwargs["author"]
