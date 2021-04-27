"""
Источник: https://5ka.ru/special_offers/
Задача организовать сбор данных,
необходимо иметь метод сохранения данных в .json файлы
результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются в Json вайлы, для каждой категории товаров должен быть создан отдельный файл и содержать товары исключительно соответсвующие данной категории.
пример структуры данных для файла:
нейминг ключей можно делать отличным от примера

{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""
import time
import json
import requests
from pathlib import Path
from urllib.parse import urlparse

start_url = 'https://5ka.ru/api/v2/special_offers/'
categories_url = 'https://5ka.ru/api/v2/categories/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:81.0) Gecko/20100101 Firefox/81.0'
}


def get_response(url, requests_headers):
    while True:
        response = requests.get(url, headers=requests_headers)
        if response.status_code == 200:
            print(f'successful request to {url}!!!')
            return response
        else:
            print(f'unsuccessful request to {url}, repeating...')
        time.sleep(0.5)


def parse_products(url, category=None):
    print(f'parsing products for {category}...')
    next_url = url
    while next_url:
        next_url = next_url.replace('monolith', urlparse(url).netloc)
        category_params = ""

        if category is not None and len(urlparse(next_url).query) == 0:
            category_params = f"?categories={category}"

        response = get_response(
            f"{next_url}{category_params}",
            headers
        )
        data = response.json()
        next_url = data['next']
        for product in data['results']:
            yield product


def parse_categories(url):
    print('parsing new category...')
    response = get_response(url, headers)
    data = response.json()
    return data


def segregate_products(category, products):
    category['products'] = list(products)
    return category


def save_json(filepath: Path, data):
    print(f'saving to file {filepath}...')
    filepath.write_text(json.dumps(data, ensure_ascii=False))


def main():
    for category in parse_categories(categories_url):
        save_json(
            Path(f"{category['parent_group_name']}.json"),
            segregate_products(
                category,
                parse_products(start_url, category['parent_group_code'])
            )
        )


main()
