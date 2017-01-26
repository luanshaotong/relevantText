#coding=utf-8
'''
Created on 2017��1��25��

@author: luan
'''

import bsddb

querystring = bsddb.btopen('querystring.db', 'c')

querycache = bsddb.btopen('cache.db','c')

#help(bsddb)

cookiecounter = bsddb.rnopen('counter.db','c')

def getCounter():
    return int(cookiecounter.get(1))

def incCounter():
    cookiecounter[1]=str(int(cookiecounter.get(1))+1)
    
def getQueryData(ident):
    return eval(querycache.get(str(ident)))

def getQueryString(ident):
    return querystring.get(str(ident))

def setQueryData(ident,data):
    querycache[str(ident)]=str(data)

def setQueryString(ident,namestr):
    querystring[str(ident)]=namestr
    
def getKey():
    return querycache.keys()
    

try:
    getCounter()
except TypeError,t:
    cookiecounter[1]='1025'
