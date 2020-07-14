import scrapy


class TescoReview(scrapy.Item):
    title = scrapy.Field()
    star_count = scrapy.Field()
    author = scrapy.Field()
    date = scrapy.Field()
    text = scrapy.Field()
