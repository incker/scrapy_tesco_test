import scrapy


class TescoReviewsBunch(scrapy.Item):
    product_id = scrapy.Field()
    page = scrapy.Field()
    reviews = scrapy.Field()
