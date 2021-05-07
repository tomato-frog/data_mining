from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from auto_youla_parse.spiders.auto_youla import AutoYoulaSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule('auto_youla_parse.settings')
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(AutoYoulaSpider)
    crawler_process.start()
