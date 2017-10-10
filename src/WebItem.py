'''
Created on 2017年10月6日

@author: luan
'''
from scrapy import Request  
from scrapy.spiders import Spider  
from scrapy.http import Request, HtmlResponse  
from scrapy.selector import Selector  
import json  
class WeiXinSpider(Spider):  
    name = 'test'  
    start_urls = [  
        'https://item.jd.com/2600240.html'  
    ]  
    global splashurl;  
    splashurl = "http://localhost:8050/render.html";# splash 服务器地址  
  
  
    #此处是重父类方法，并使把url传给splash解析  
    def make_requests_from_url(self, url):  
        global splashurl;  
        url=splashurl+"?url="+url;  
        #body = json.dumps({"url": url, "wait": 5, 'images': 0, 'allowed_content_types': 'text/html; charset=utf-8'})  
        headers = {'Content-Type': 'application/json'}  
        return Request(url, body=body,headers=headers,dont_filter=True)  
  
    def parse(self, response):  
        print "############"+response._url  
  
        fo = open("jdeeeeeeeeee.html", "wb")  
        fo.write(response.body);  # 写入文件  
        fo.close();  
        '''''site = Selector(response) 
        links = site.xpath('//a/@href') 
        for link in links: 
            linkstr=link.extract() 
            print "*****"+linkstr 
            yield SplashRequest(linkstr, callback=self.parse)'''  