# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TeachesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    school_level = scrapy.Field()
    school = scrapy.Field()
    name = scrapy.Field()
    title = scrapy.Field()
    school_college = scrapy.Field()
    url = scrapy.Field()
    email = scrapy.Field()
    resh_dict = scrapy.Field()

