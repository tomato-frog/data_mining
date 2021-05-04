from .models import (
    Comment,
    Author
)


def get_instance_by(filter_field):
    def get_instance(Model, session, **data):
        instance = session.query(Model).filter_by(**{filter_field: data[filter_field]}).first()

        return instance or Model(**data)

    return get_instance


get_by_id = get_instance_by('id')
get_by_url = get_instance_by('url')


def process_comments(comments, session):
    for comment in map(
        lambda item: item['comment'],
        comments
    ):
        author = get_by_id(
            Author,
            session,
            name=comment['user']['full_name'],
            url=comment['user']['url'],
            id=comment['user']['id'],
        )

        session.add(author)

        comment_instance = get_by_id(
            Comment,
            session,
            **comment,
            author=author,
        )

        session.add(comment_instance)

        yield comment_instance

        yield from process_comments(comment['children'], session)
