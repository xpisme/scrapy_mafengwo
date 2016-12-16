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

class info(scrapy.Spider):
    name = "info"
    base_url = 'http://www.mafengwo.cn'
    allowed_domains = ["www.mafengwo.cn"]
    start_urls = []
    headers = {
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch, br',
        'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Host':'www.mafengwo.cn',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36',
        "Referer": "https://www.mafengwo.cn",
        "Origin" : "https://www.mafengwo.cn"
    }

    def start_requests(self):
        #重写了爬虫类的方法, 实现了自定义请求, 运行成功后会调用callback回调函数
        print '--------------------start request------------------'
        while (True):
            time.sleep(1.5)
            request_url = self.get_url()
            if request_url:
                print request_url
                yield scrapy.Request(url=request_url, 
                callback=self.parse_item, 
                dont_filter=True, 
                errback=self.errback_httpbin)

    def get_url(self):
        self.master_db = DB(MySQL['db_host'], MySQL['db_port'], MySQL['db_user'], MySQL['db_password'], MySQL['db_dbname']) 
        sql = """select * from scenic where status = 0 limit 1"""
        res = self.master_db.query(sql, ())
        if not res:
            self.master_db.__delete__()
            return False
        url = res[0]['url']
        sql = """update scenic set status = 2 where id = %s"""
        self.master_db.execute(sql, (res[0]['id']))
        request_url = self.base_url + url
        return request_url

    def errback_httpbin(self, failure):
        url = failure.request.url
        print failure
        sql = """update scenic set status = 3 where url = %s"""
        self.master_db.execute(sql, (url[22:]))
        self.master_db.__delete__()


    def parse_item(self, response):
        print '++++++++++++++++++++++++++++++++++++++++++'
        item_url = response.url[22:].encode('utf-8')
        item_location = response.css('.mod-location .mhd .sub::text')[0].extract().encode('utf-8')
        item_summary = response.css('.summary')[0].extract().encode('utf-8') if len(response.css('.summary')) else 0
        sql = "insert into scenic_info (url, location, summary) values (%s, %s, %s)"
        resQuery = self.master_db.execute(sql, (item_url, item_location, item_location))
        self.master_db.execute('update scenic set status = 1 where url = %s', (item_url))
        self.master_db.__delete__()
