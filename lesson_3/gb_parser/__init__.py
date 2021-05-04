from urllib.parse import urljoin

from .util import get_soup, gather_nested, get_response

blog_url = 'https://gb.ru/posts'


def comments_url(post_id):
    return f'https://gb.ru/api/v2/comments' \
           f'?commentable_type=Post&commentable_id={post_id}&order=desc'


async def parse_pages_amount(url):
    soup = await get_soup(url)
    links = soup.select('.gb__pagination a')
    return int(links[-2].text)


async def parse_post_links(url, page: int):
    page_link = f'{url}?page={page}'
    soup = await get_soup(page_link)
    post_items = soup.select('.post-item.event')

    return [
        urljoin(url, post.find('a', href=True).get('href'))
        for post in post_items
    ]


async def parse_post(url):
    soup = await get_soup(url)
    author_tag = soup.select_one('[itemprop="author"]')
    first_img = soup.select_one('.blogpost-content img')
    id_element = soup.select_one('.referrals-social-buttons-small-wrapper')
    post_id = id_element.attrs.get('data-minifiable-id')

    return {
        'gb_id': post_id,
        'url': url,
        'title': soup
            .select_one('.blogpost-title')
            .text,

        'first_picture_link': first_img.attrs.get('src') if first_img else None,

        'date_of_publishing': soup
            .select_one('.blogpost-date-views > time')
            .attrs['datetime'],

        'author': {
            'name': author_tag.text,
            'url': urljoin(url, author_tag.parent.attrs.get('href')),
        },
        'comments': await parse_comments(post_id),
        'tags': [
            {
                'name': tag.text,
                'url': urljoin(url, tag.attrs.get('href'))
            }
            for tag in soup.find_all("a", attrs={"class": "small"})
        ]
    }


async def parse_comments(post_id):
    response = await get_response(comments_url(post_id))
    return response.json()


async def parse_posts(url, page):
    return [
        parse_post(link)
        for link in await parse_post_links(url, page)
    ]


async def parse_gb_blog(url):
    pages = await parse_pages_amount(url)

    return await gather_nested(
        parse_posts(url, page)
        for page in range(pages)
    )
