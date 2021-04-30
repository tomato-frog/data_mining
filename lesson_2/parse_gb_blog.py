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
import time
import bs4
from urllib.parse import urljoin


client = pymongo.MongoClient()
start_url = 'https://gb.ru/posts'

######


def get_response(url):
    while True:
        response = requests.get(url)
        if response.status_code == 200:
            print(f'successful request to {url}!!!')
            return response
        else:
            print(f'unsuccessful request to {url}, repeating...')
        time.sleep(0.5)


def get_soup(url):
    soup = bs4.BeautifulSoup(get_response(url).text, 'lxml')
    return soup

#####


def get_pages_amount(url):
    soup = get_soup(url)
    pagination = soup.find('ul', attrs={'class': 'gb__pagination'})
    links = pagination.find_all('a')
    pages_amount = int(links[-2].text)
    return pages_amount


def get_posts_links(page: int):
    page_link = f'{start_url}?page={page}'
    soup = get_soup(page_link)
    post_item_events = soup.find_all('div', attrs={'class': 'post-item event'})
    for post_item_event in post_item_events:
        yield urljoin(start_url, post_item_event.find('a', href=True).get('href'))


def get_post_info(url):
    soup = get_soup(url)
    author_tag = soup.find('div', attrs={'itemprop': 'author'})
    first_img = soup.find("div", attrs={"class": "blogpost-content"}).find("img")

    data = {
        'url': url,
        'title': soup
            .find('h1', attrs={'class': 'blogpost-title'})
            .text,
        'first_picture_link': first_img.attrs.get('src') if first_img else None,

        'date_of_publishing': soup
            .find('div', attrs={'class': 'blogpost-date-views'})
            .find('time')
            .attrs['datetime'],

        'author_name': author_tag.text,
        'author_url': urljoin(url, author_tag.parent.attrs.get("href")),
    }
    return data


def parse_posts(page):
    for link in (get_posts_links(page)):
        yield get_post_info(link)


def save_to_mongodb(post_info):
    collection = client['gb']['gb_blog']
    collection.insert_one(post_info)


def main():
    for page in range(get_pages_amount(start_url)):
        for post in (list(parse_posts(page))):
            save_to_mongodb(post)


main()
