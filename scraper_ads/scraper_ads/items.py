# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AdItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ad_id = scrapy.Field()
    ad_url = scrapy.Field()
    youtube_url = scrapy.Field()
    pass
