import scrapy


class TescoAdviceProduct(scrapy.Item):
    product_url = scrapy.Field()
    product_title = scrapy.Field()
    image_url = scrapy.Field()
    price = scrapy.Field()
