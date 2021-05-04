from .models import (
    Comment,
    Author
)


def get_instance_by(filter_field):
    def get_instance(model, session, **data):
        return session.query(model).filter_by(filter_field=data[filter_field]).first()\
               or model(**data)

    return get_instance


get_by_id = get_instance_by('id')


def process_comments(comments, session):
    for comment in comments:
        author = get_by_id(
            Author,
            session,
            name=comment['comment']['user']['full_name'],
            url=comment['comment']['user']['url'],
            id=comment['comment']['user']['id'],
        )

        yield get_by_id(
            Comment,
            session,
            **comment['comment'],
            author=author,
        )

        yield from process_comments(comment['comment']['children'], session)
