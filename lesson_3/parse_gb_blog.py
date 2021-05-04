from asyncio import run

from lesson_3.database import Database
from lesson_3.gb_parser import parse_gb_blog, blog_url


if __name__ == '__main__':
    database = Database('sqlite:///gb_blog.db')
    posts = run(parse_gb_blog(blog_url))

    database.insert_posts(posts)
