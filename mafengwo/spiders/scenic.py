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

class scenic(scrapy.Spider):
    name = "scenic"
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
        write_db = DB(MySQL['db_host'], MySQL['db_port'], MySQL['db_user'], MySQL['db_password'], MySQL['db_dbname']) 
        res_list = write_db.query('select country_id from country where status = 0', ())
        for j in res_list:
            time.sleep(randint(3, 5))
            yield scrapy.Request(url = """http://www.mafengwo.cn/jd/""" + str(j['country_id']) + """/gonglve.html""", headers = self.headers, callback = self.parse_item)
        #重写了爬虫类的方法, 实现了自定义请求, 运行成功后会调用callback回调函数

    def parse_item(self, response):
        write_db = DB(MySQL['db_host'], MySQL['db_port'], MySQL['db_user'], MySQL['db_password'], MySQL['db_dbname']) 
        tmp_res = response.url.split('/')
        country_id = tmp_res[-2]
        item = MafengwoItem() 
        scenics = response.css('.row-allPlace li a')
        for i in scenics:
            item['cn_name'] = i.css('a strong::text').extract()
            item['en_name'] = i.css('a::text').extract()
            item['url'] = i.css('a::attr("href")').extract()
            print '------==========------------========-------======='
            item['cn_name'] = item['cn_name'][0].encode('utf-8').strip() if item['cn_name'] else 0
            item['en_name'] = item['en_name'][0].encode('utf-8').strip() if item['en_name'] else 0
            item['url'] = item['url'][0].encode('utf-8') if item['url'] else 0
            if item['cn_name']:
                print item
                sql = "insert ignore into scenic (cn_name, en_name, url, country_id) values (%s, %s, %s, %s)"
                resQuery = write_db.execute(sql, (item['cn_name'], item['en_name'], item['url'], country_id))

        write_db.execute('update country set status = 1 where country_id = %s', (str(country_id)))
        write_db.__delete__()
