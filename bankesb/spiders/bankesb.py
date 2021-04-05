import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankesb.items import Article


class bankesbSpider(scrapy.Spider):
    name = 'bankesb'
    start_urls = ['https://www.bankesb.com/about/news/']

    def parse(self, response):
        links = response.xpath('//a[@class="cta-btn"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="article-date"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//article[@class="mod-news-details"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content[1:-1]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
