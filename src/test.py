#coding=utf-8
'''
Created on 2017��1��18��

@author: luan
'''
import requests


from bs4 import BeautifulSoup

import sys

sys.setdefaultencoding='utf-8'

xsurl = 'http://xueshu.baidu.com/s?wd='

scurl = 'https://scholar.google.com/scholar?hl=zh-CN&as_sdt=0%2C5&q=hello&btnG='

splashurl = 'http://localhost:8050/render.html'

    
def startSearch(queryStr):
    
    body = requests.get(splashurl+'?url='+xsurl+queryStr)
    
    soup = BeautifulSoup(body.text.encode('utf-8'),'html5lib')
    
    contents = soup.select('.sc_content')
    
    data = []
    
    ct = 1
    
    print 'lllll\n'
    
    for tagA in contents :
        print '\n##index' + str(ct)
        ct += 1
        piece = {}
        piece['url'] = tagA.h3.a.get('href').encode('ascii')
        piece['title'] = ' '.join(tagA.h3.a.stripped_strings).encode('ascii','ignore')
        piece['description'] = ' '.join(tagA.find(class_='c_abstract').stripped_strings).split(u'来')[0].encode('ascii','ignore')
        piece['rel'] = False
        data.append(piece)
        print piece
    
    return data

file = open('test.txt','w')

