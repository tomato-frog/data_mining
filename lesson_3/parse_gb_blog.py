from asyncio import run, ensure_future, gather
from time import time

from lesson_3.database import Database
from lesson_3.gb_parser import parse_gb_blog, blog_url

total_posts = 0


def increment_total():
    global total_posts
    total_posts += 1
    print(f'\rSaving {total_posts} posts...', end='')


async def main():
    print('Opening database connection...')
    database = Database('sqlite:///gb_blog.db')

    times = []

    print('Parsing blog...')

    blog = parse_gb_blog(blog_url, increment_total)

    print('Parsing posts...')

    async for future_posts in blog:
        start_time = time()
        posts = await future_posts
        database.insert_posts(posts)
        times.append((time() - start_time)/30)
        print(f'\rSaved {total_posts} posts...', end='')

    print(
        'Done!\nAverage time per post:',
        '{:.2f}'.format(sum(times) / len(times)),
        'seconds'
    )

if __name__ == '__main__':
    run(main())
