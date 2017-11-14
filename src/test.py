#coding=utf-8
'''
Created on 2017��1��18��

@author: luan
'''
import requests

import bsddb

import os

import sys

import traceback

import configuration

import json

import re

from operator import itemgetter

count = 0
try:
    from gensim import corpora
    
    from gensim import models
    
    from gensim import similarities
    
    from model import trainw2vmodel,traindoc2vecmodel,trainmodel
    
    from formatfile import getCorpus,adjustrank,queryrelevantdocs,preprocess,getabs,removepunctuation

    
except Exception,e :
    traceback.print_exc(file=sys.stdout)
    count = 1


from bs4 import BeautifulSoup

from commonMethods import quote


#from lxml.html._diffcommand import description

 
query = 'hello'

xsurl = 'http://xueshu.baidu.com/s?wd='

scurl = 'https://xues.glgoo.com/scholar?num=20&as_sdt=0&q='

splashurl = 'http://localhost:8050/render.html'

headers = { "Accept":"text/html,application/xhtml+xml,application/xml;",
            "Accept-Encoding":"gzip",
            "Accept-Language":"zh-CN,zh;q=0.8",
            "Referer":"http://www.example.com/",
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
            }

topN = 5

existedflag = True
datasettype = 'citeulike'  # 'nips'#
datadir = configuration.trainpath
trainingset = datadir + 'abs'
stemflag = True
modeldir = configuration.modelpath
num_topics = 200
trainflag = False
modelflag = 'lsi'  #'lsi'#
#1 is topic sims,2 is topic sims plus author sims
simflag=1
#start = time()
docs, corpus, dictionary = getCorpus(
                                          existedflag,\
                                          datasettype,\
                                          trainingset,\
                                          datadir,\
                                          stemflag)
topicmodel = trainmodel(datasettype, trainflag, modelflag, num_topics, corpus, dictionary,modeldir)
topicindex = similarities.MatrixSimilarity(topicmodel[corpus])

def getStdRef(title):
    start_urls = ('http://xueshu.baidu.com/s?wd=paperuri%3A%28fe9f6db90244429441fc74a08f240f9d%29&filter=sc_long_sign&sc_ks_para=q%3DReinforcement%20Learning%3A%20A%20Survey&sc_us=2693735548158023755&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8')
    script = """ 
        function main(splash)
            splash:go(splash.args.url)
            local title = splash:select('.t>a')
            if title~=nil then
                splash:go('http://xueshu.baidu.com'..title:getAttribute('href'))
            end
            local elem = splash:select('.sc_q')
            elem:mouse_click()
            splash:wait(0.5)
            return splash:select('.sc_quote_list_item_r[data-type="APA"]').text()
        end
        """
        
    splashendpoint = 'http://localhost:8050/execute'
    body = requests.get(splashendpoint+'?url='+quote(xsurl+title), headers=headers,params={
                    'lua_source':script
            }).text
    #body = requests.get(splashurl+'?url='+quote(start_urls), headers=headers) 
    #print body.text
    #soup = BeautifulSoup(body.text.encode('utf-8'),'html5lib')
    
    #print soup.find_all(class_='sc_quote_list_item_r')
    if body[0]=='{':
        return 'Not available.'
    else :
        return body

def getData_baidu(soup):
    
    contents = soup.select('.sc_content')
    
    data = []
    
    ct = 1
    
    print 'lllll\n'
    
    for tagA in contents :
        #print '\n##index' + str(ct)
        ct += 1
        piece = {}
        piece['url'] = 'http://xueshu.baidu.com' +tagA.h3.a.get('href').encode('ascii')
        piece['title'] = ' '.join(tagA.h3.a.stripped_strings).encode('ascii','ignore')
        piece['description'] = ' '.join(tagA.find(class_='c_abstract').stripped_strings).split(u'来')[0].encode('ascii','ignore')
        piece['rel'] = False
        data.append(piece)
        #print piece
    
    return data

def getData_google(soup):
    
    contents = soup.find(id = 'gs_res_ccl_mid')
    
    data = []
    
    ct = 1
    
    print 'lllll\n'
    
    for tagA in contents :
        #print '\n##index' + str(ct)
        ct += 1
        piece = {}
        piece['url'] = tagA.find(class_='gs_rt').a.get('href').encode('ascii')
        piece['title'] = ' '.join(tagA.find(class_='gs_rt').stripped_strings).encode('ascii','ignore')
        piece['description'] = ' '.join(tagA.find(class_='gs_rs').stripped_strings).encode('ascii','ignore')
        piece['rel'] = False
        data.append(piece)
        #print piece
    
    return data
    
def startSearch(queryStr):
    
    body = requests.get(splashurl+'?url=' +quote(scurl+queryStr), headers=headers )
    print body.text
    
    soup = BeautifulSoup(body.text.encode('utf-8'),'html5lib')
    
    data = getData_baidu(soup)

    body = requests.get(splashurl+'?url=' +quote( scurl+queryStr +'&start=20'),headers=headers )
    #body = requests.get(splashurl+'?url=' + xsurl+queryStr +'&pn=10&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&sc_hit=1' )
    
    #print body.text
    
    soup = BeautifulSoup(body.text.encode('utf-8'),'html5lib')
    
    for i in getData_baidu(soup):
        data.append(i)
    
    return data
    
def startSearch_local(queryStr):

    query = preprocess(queryStr)
    query2bow = dictionary.doc2bow(query)
    qtopics = topicmodel[query2bow]
    #print 'docs', docs
    
    print 'topicmodel',topicmodel
    print 'query2bow',query2bow
    print 'qtopics ', qtopics
    sims = topicindex[qtopics]
    sims = sorted(enumerate(sims), lambda x, y: cmp(x[1], y[1]), reverse=True)
    return zip(*sims)[0],query
    print 'sims',sims


if count ==0 :
    def adjustQuery(query,data,irdocs):
        
        reltexts = []
        irreltexts = []
        docs = []
        for piece in irdocs :
            if piece['rel']:
                reltexts.append(piece['description'])
            else :
                irreltexts.append(piece['description'])
        
        #query = preprocess(queryStr)
        #query2bow=dictionary.doc2bow(query)
        #qtopics = model[query2bow]
        
        #return adjustrank(model,dictionary,qtopics,docs,topN,reltexts,irreltexts)
        return adjustrank(topicmodel,topicindex, dictionary,query,reltexts,irreltexts)
else :
    def adjustQuery(queryStr,docs,data):
        return [3,5]

if __name__ == '__main__':
    #startSearch_local('reinforcement learning a survey')
    #print getStdRef('reinforcement learning a survey')
    
    #os.remove(configuration.modelpath+'abs.db')
    abshash = bsddb.hashopen(configuration.modelpath+'abs.db','c')

#adjustQuery('hello', [])
