import scrapy


class TescoProduct(scrapy.Item):
    url = scrapy.Field()
    id = scrapy.Field()
    image_url = scrapy.Field()
    title = scrapy.Field()
    category = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    name_and_address = scrapy.Field()
    return_address = scrapy.Field()
    net_contents = scrapy.Field()
    advice_products = scrapy.Field()
