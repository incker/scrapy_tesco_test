import re
import time
from decimal import Decimal

import scrapy

from items.tesco_advice_product import TescoAdviceProduct
from items.tesco_product import TescoProduct
from items.tesco_review import TescoReview
from items.tesco_reviews_bunch import TescoReviewsBunch
import logging


class QuotesSpider(scrapy.Spider):
    name = "tesco"
    allowed_domains = ['tesco.com']
    custom_settings = {'REDIRECT_MAX_TIMES': 0}

    def __init__(self, url=None, *args, **kwargs):
        super(QuotesSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
        else:
            logging.error('Provide a correct url to command line to crawl, like: `-a url="..."` ')
            self.start_urls = []

    def parse(self, response):
        logging.info("Product list page received: " + response.url)

        product_list = response.css('.product-list')
        product_links = product_list.xpath('//h3/a')

        yield from response.follow_all(product_links, self.parse_product)
        pagination_links = response.xpath("//nav[@class='pagination--page-selector-wrapper']//a")
        yield from response.follow_all(pagination_links, self.parse)

    def parse_product(self, response):
        product_id = QuotesSpider.product_id_from_url(response.url)
        product_main_block = response.css('.product-details-tile')

        try:
            price = Decimal(response.xpath("//span[@data-auto='price-value']/text()").get())
        except TypeError:
            price = None

        tesco_product = TescoProduct()

        tesco_product['url'] = response.url
        tesco_product['id'] = product_id
        tesco_product['image_url'] = product_main_block.xpath('.//img/@src').get()
        tesco_product['title'] = product_main_block.xpath('.//h1/text()').get()
        tesco_product['category'] = response.xpath("//nav[@aria-label='breadcrumb']//text()").getall().pop()
        tesco_product['price'] = price,
        tesco_product['description'] = ' '.join(filter(lambda s: s, [
            *response.xpath("//div[@id='product-marketing']//text()").getall(),
            response.xpath("//div[@id='brand-marketing']//text()").get(),
            response.xpath("//div[@id='other-information']//text()").get(),
            response.xpath("//div[@id='pack-size']//text()").get(),
        ])),
        tesco_product['name_and_address'] = ' '.join(
            response.xpath("//div[@id='manufacturer-address']/ul//text()").getall())
        tesco_product['return_address'] = ' '.join(response.xpath("//div[@id='return-address']/ul//text()").getall())
        tesco_product['net_contents'] = response.xpath("//div[@id='net-contents']/p/text()").get()
        tesco_product['advice_products'] = QuotesSpider.parse_advice_products(response)

        yield tesco_product

        yield from self.parse_review_urls(response, product_id)

    @staticmethod
    def product_id_from_url(url: str):
        match = re.search(r'/(\d+)$', url)
        return int(match[1]) if match else None

    @staticmethod
    def parse_advice_products(response):
        recommender = response.xpath("//div[@class='recommender__wrapper']")
        arr = []
        for product_tile in recommender.xpath("div[@class='product-tile-wrapper']"):
            advice_product = TescoAdviceProduct()
            advice_product['product_url'] = response.urljoin(product_tile.xpath('.//h3/a/@href').get())
            advice_product['product_title'] = product_tile.xpath('.//h3/a/text()').get()
            # url is absolute by default
            advice_product['image_url'] = product_tile.xpath('.//img/@src').get()
            advice_product['price'] = float(product_tile.xpath(".//span[@class='value']/text()").get())
            arr.append(advice_product)
        return arr

    def parse_review_urls(self, response, product_id):
        base_review_url = response.url.replace("products", "reviews")

        try:
            review_count = int(response.xpath("//div[@id='review-data']/section/h4/text()").re(r'\d+')[0])
        except IndexError:
            # no reviews
            return

        # each page has 10 reviews
        page_count = review_count // 10 + (1 if review_count % 10 else 0)

        for page_num in range(1, page_count + 1):
            # url = urlparse.urljoin(base_review_url, 'page=2')
            url = base_review_url + '?page=' + str(page_num)
            url = 'https://www.tesco.com/groceries/en-GB/reviews/83164520' + '?page=' + str(page_num)
            yield scrapy.Request(url,
                                 headers={'accept': 'application/json'},
                                 cb_kwargs=dict(product_id=product_id),
                                 callback=self.parse_review_data)

    def parse_review_data(self, response, product_id):
        # test data response in scrapy shell:
        # fetch("https://www.tesco.com/groceries/en-GB/reviews/83164520?page=2", redirect=False, headers={'accept': 'application/json'})
        json = response.json()

        reviews = []

        for raw_review in json['entries']:
            time_posted = time.localtime(raw_review['submissionTime'] / 1000)
            review_date_str = time.strftime('%Y-%m-%d %H:%M:%S', time_posted)

            review = TescoReview()
            review['title'] = raw_review['summary']
            review['star_count'] = raw_review['rating']['value']
            review['author'] = raw_review['syndicationSource']['clientId']
            review['date'] = review_date_str
            review['text'] = raw_review['text']
            reviews.append(review)

        reviews_bunch = TescoReviewsBunch()
        reviews_bunch['product_id'] = product_id
        reviews_bunch['page'] = json['info']['page']
        reviews_bunch['reviews'] = reviews

        yield reviews_bunch
