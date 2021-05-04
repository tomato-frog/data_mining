from asyncio import get_event_loop
from signal import SIGINT, SIGTERM
from time import time

from lesson_3.database import Database
from lesson_3.gb_parser import parse_gb_blog, blog_url

total_posts = 0
saved_posts = 0


def increment_total():
    global total_posts
    total_posts += 1
    print(f'\rSaving {total_posts} posts...', end='')


async def main():
    global saved_posts
    times = []

    print('Opening database connection...')
    database = Database('sqlite:///gb_blog.db')

    print('Parsing blog...', end='')
    t = time()
    blog = await parse_gb_blog(blog_url, increment_total)
    print(f'\rParsed blog in {"{:.2f}".format(time() - t)} sec')

    print('Parsing posts...')
    for future_posts in blog:
        start_time = time()
        posts = await future_posts
        database.insert_posts(posts)
        times.append((time() - start_time)/30)
        saved_posts += len(posts)
        print(f'\rSaved {total_posts} posts...', end='')

    print(
        'Done!\nAverage time per post:',
        '{:.2f}'.format(sum(times) / len(times)),
        'sec'
    )

if __name__ == '__main__':
    def graceful_shutdown():
        main_task.cancel()
        print('\nInterrupted...')
        print(f'\nSaved {saved_posts} posts.')
        exit(0)

    try:
        loop = get_event_loop()
        main_task = loop.create_task(main())

        for signal in [SIGINT, SIGTERM]:
            loop.add_signal_handler(signal, graceful_shutdown)

        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        graceful_shutdown()
