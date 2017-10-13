#coding=utf-8
'''
Created on 2017��1��18��

@author: luan
'''
import requests

import sys

import traceback

count = 0
try:
    from gensim import corpora
    
    from gensim import models
    
    from feedbackprocess import adjustrank
    
    from feedbackprocess import preprocess
    
except Exception,e :
    traceback.print_exc(file=sys.stdout)
    count = 1


from bs4 import BeautifulSoup


#from lxml.html._diffcommand import description

 
query = 'hello'

xsurl = 'http://xueshu.baidu.com/s?wd='

scurl = 'https://scholar.google.com/scholar?hl=zh-CN&num=20&as_sdt=0&q='

splashurl = 'http://localhost:8050/render.html'


topN = 5

def getData_baidu(soup):
    
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

def getData_google(soup):
    
    contents = soup.find(id = 'gs_res_ccl_mid')
    
    data = []
    
    ct = 1
    
    print 'lllll\n'
    
    for tagA in contents :
        print '\n##index' + str(ct)
        ct += 1
        piece = {}
        piece['url'] = tagA.find(class_='gs_rt').a.get('href').encode('ascii')
        piece['title'] = ' '.join(tagA.find(class_='gs_rt').stripped_strings).encode('ascii','ignore')
        piece['description'] = ' '.join(tagA.find(class_='gs_rs').stripped_strings).encode('ascii','ignore')
        piece['rel'] = False
        data.append(piece)
        print piece
    
    return data
    
def startSearch(queryStr):
    
    body = requests.get(splashurl+'?url='+scurl+queryStr)
    
    print body.text
    
    soup = BeautifulSoup(body.text.encode('utf-8'),'html5lib')
    
    return getData_google(soup)


if count ==0 :
    def adjustQuery(queryStr,data,irdocs):
        
        model = models.LsiModel.load('trainlsiciteulikemodel',mmap='r')
        dictionary = corpora.Dictionary.load('trainciteulikedict')
        reltexts = []
        irreltexts = []
        docs = []
        for piece in irdocs :
            if piece['rel']:
                reltexts.append(piece['title']+piece['description'])
            else :
                irreltexts.append(piece['title']+piece['description'])
        for piece in data:
            docs.append(piece['title']+piece['description'])
        
        
        
        query = preprocess(queryStr)
        query2bow=dictionary.doc2bow(query)
        qtopics = model[query2bow]
        
        return adjustrank(model,dictionary,qtopics,docs,topN,reltexts,irreltexts)
else :
    def adjustQuery(queryStr,docs,data):
        return [3,5]

#startQuery('hello')

#adjustQuery('hello', [])
