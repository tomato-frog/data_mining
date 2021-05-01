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
import pymongo
import requests
import bs4
from urllib.parse import urljoin
from asyncio import gather, get_event_loop, run, sleep

client = pymongo.MongoClient()
start_url = 'https://gb.ru/posts'


######


def do_async(f, *args):
    return get_event_loop().run_in_executor(None, f, *args)


async def get_response(url):
    while True:
        response = await do_async(requests.get, url)

        if response.status_code == 200:
            return response

        await sleep(0.5)


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

    return {
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
    }


async def parse_posts(url, page):
    return [
        get_post_info(link)
        for link in await get_posts_links(url, page)
    ]


def save_to_mongodb(post_info):
    collection = client['gb']['gb_blog']
    collection.insert_one(post_info)


async def main():
    posts_parsed = 0

    print('Parsing amount of pages...')
    pages = await get_pages_amount(start_url)

    print('Parsing post links from', pages, 'pages...')
    posts_per_page = await gather(*[
        parse_posts(start_url, page)
        for page in range(pages)
    ])

    print('Parsing posts from', pages, 'pages...')
    for posts in posts_per_page:
        for post in await gather(*posts):
            save_to_mongodb(post)
            posts_parsed += 1
            print('\rParsed', posts_parsed, 'posts from', pages, 'pages', end='')

try:
    run(main())
finally:
    print('\nDone!')
