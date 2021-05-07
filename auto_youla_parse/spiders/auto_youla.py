import scrapy


class AutoYoulaSpider(scrapy.Spider):
    name = 'auto_youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    def parse(self, response):
        pass
