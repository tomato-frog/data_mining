"""
Источник https://gb.ru/posts/
Необходимо обойти все записи в блоге и извлечь из них информацию следующих полей:
- url страницы материала
- Заголовок материала
- Первое изображение материала (Ссылка)
- Дата публикации (в формате datetime)
- имя автора материала
- ссылка на страницу автора материала
- комментарии в виде (автор комментария и текст комментария)
Структуру сохраняем в MongoDB
"""
from time import time
import pymongo
import requests
import bs4
from urllib.parse import urljoin
from asyncio import gather, get_event_loop, run, sleep

client = pymongo.MongoClient()
start_url = 'https://gb.ru/posts'


def comments_url(post_id):
    return f'https://gb.ru/api/v2/comments' \
           f'?commentable_type=Post&commentable_id={post_id}&order=desc'


######


def calc_time(start_time):
    return f' {"{:.1f}".format(time() - start_time)} seconds'


def do_async(f, *args):
    return get_event_loop().run_in_executor(None, f, *args)


async def get_response(url):
    while True:
        response = await do_async(requests.get, url)

        if response.status_code == 200:
            return response

        await sleep(2)


async def get_soup(url):
    response = await get_response(url)
    return bs4.BeautifulSoup(response.text, 'lxml')


#####


async def get_pages_amount(url):
    soup = await get_soup(url)
    links = soup.select('.gb__pagination a')
    return int(links[-2].text)


async def get_posts_links(url, page: int):
    page_link = f'{url}?page={page}'
    soup = await get_soup(page_link)
    post_items = soup.select('.post-item.event')

    return [
        urljoin(start_url, post.find('a', href=True).get('href'))
        for post in post_items
    ]


async def get_post_info(url):
    soup = await get_soup(url)
    author_tag = soup.select_one('[itemprop="author"]')
    first_img = soup.select_one('.blogpost-content img')
    id_element = soup.select_one('.referrals-social-buttons-small-wrapper')
    post_id = id_element.attrs.get('data-minifiable-id')

    return {
        'id': post_id,
        'url': url,
        'title': soup
            .select_one('.blogpost-title')
            .text,

        'first_picture_link': first_img.attrs.get('src') if first_img else None,

        'date_of_publishing': soup
            .select_one('.blogpost-date-views > time')
            .attrs['datetime'],

        'author_name': author_tag.text,
        'author_url': urljoin(url, author_tag.parent.attrs.get('href')),
        'comments': (await get_response(comments_url(post_id))).json()
    }


async def parse_posts(url, page):
    return [
        get_post_info(link)
        for link in await get_posts_links(url, page)
    ]


def save_to_mongodb(posts):
    collection = client['gb']['gb_blog']
    collection.insert_many(posts)


async def main():
    print('Parsing amount of pages...')
    pages = await get_pages_amount(start_url)

    print('Parsing post links from', pages, 'pages...', end='')
    start_time = time()
    posts_per_page = await gather(*[
        parse_posts(start_url, page)
        for page in range(pages)
    ])
    print(calc_time(start_time))

    total_posts = 0

    print('Parsing posts from', pages, 'pages...', end='')
    start_time = time()
    for future_posts in posts_per_page:
        posts = await gather(*future_posts)
        total_posts += len(posts)
        save_to_mongodb(posts)
        print('\rSaved', total_posts, 'posts to database...', end='')

    print('\rSaved', total_posts, 'posts to database in', calc_time(start_time))


try:
    run(main())
finally:
    print('\nDone!')
