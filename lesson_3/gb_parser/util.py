import requests
import bs4

from asyncio import gather, get_event_loop, sleep


######
def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


async def gather_nested(deep_coroutines):
    return await gather(*flatten(await gather(*list(deep_coroutines))))


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

