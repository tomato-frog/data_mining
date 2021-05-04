from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as create_session
from .util import get_instance_by, get_by_id, process_comments
from .models import (
    Base,
    Post,
    Author,
    Tag,
    Comment
)


class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = create_session(self.engine)

    def insert_posts(self, posts):
        with self.Session() as session:
            for post_data in posts:
                post = get_by_id(
                    Post,
                    session,
                    **post_data
                )
                author = get_by_id(Author, session, **post_data['author'])
                tags = map(
                    lambda tag: get_instance_by('url')(Tag, session, **tag),
                    post_data['tags']
                )

                post.author = author
                post.tags.extend(tags)
                post.comments.extend(process_comments(
                    post_data['comments'],
                    session
                ))

                try:
                    session.add(post)
                    session.commit()
                except IntegrityError as error:
                    print(error)
                    session.rollback()
