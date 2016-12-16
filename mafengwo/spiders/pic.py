# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from mafengwo.items import MafengwoItem
from mafengwo.settings import MySQL
from random import randint
from imysql import DB
import scrapy
import json
import codecs
import time

class pic(scrapy.Spider):
    name = "pic"
    base_url = 'http://www.mafengwo.cn/mdd/ajax_photolist.php?act=getPoiPhotoList&poiid='
    allowed_domains = ["www.mafengwo.cn"]
    start_urls = []

    def start_requests(self):
        #重写了爬虫类的方法, 实现了自定义请求, 运行成功后会调用callback回调函数
        print '--------------------start request------------------'
        while (True):
            time.sleep(2.5)
            request_url = self.get_url()
            if request_url:
                print request_url
                yield scrapy.Request(url=request_url, 
                callback=self.parse_item, 
                dont_filter=True, 
                errback=self.errback_httpbin)

    def get_url(self):
        self.master_db = DB(MySQL['db_host'], MySQL['db_port'], MySQL['db_user'], MySQL['db_password'], MySQL['db_dbname']) 
        sql = """select * from scenic_info where pic_list is null limit 1"""
        res = self.master_db.query(sql, ())
        if not res:
            self.master_db.__delete__()
            return False
        url = res[0]['url']
        request_url = self.base_url + url[5:url.index('.')]
        return request_url

    def errback_httpbin(self, failure):
        self.master_db.__delete__()


    def parse_item(self, response):
        print '++++++++++++++++++++++++++++++++++++++++++'
        item_url = response.url
        item_url = "/poi/" + item_url[item_url.index('d=') + 2:].encode('utf-8') + ".html"  
        res_pic_list = response.css('.column .cover img::attr("src")').extract()
        item_pic_list = ","
        for i in res_pic_list:
            item_pic_list = item_pic_list + i[0:i.index('?')].encode('utf-8') +  "," 
        print item_pic_list
        print item_url
        sql = "update scenic_info set pic_list = %s where url = %s"
        resQuery = self.master_db.execute(sql, (item_pic_list, item_url))
        self.master_db.__delete__()
