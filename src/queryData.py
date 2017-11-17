#coding=utf-8
'''
Created on 2017��1��25��

@author: luan
'''

import bsddb

import configuration

querystring = bsddb.btopen('querystring.db', 'c')

querycache = bsddb.btopen('cache.db','c')

queryrank = bsddb.btopen('ranks.db','c')

queryrel = bsddb.btopen('rel.db','c')

querydown = bsddb.btopen('down.db','c')

queryfktemp = bsddb.btopen('temp.db','c')

abshash = bsddb.hashopen(configuration.modelpath+'abs.db','c')
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

def getQueryRel(ident):
    return eval(queryrel.get(str(ident)))

def getQueryDown(ident):
    return eval(querydown.get(str(ident)))

def getQueryTemp(ident):
    return eval(queryfktemp.get(str(ident)))

def getQueryRank(ident):
    #print queryrank.get(str(ident))
    return eval(queryrank.get(str(ident)))

def getRelatext(index):
    #print ranks
    return eval(abshash.get(str(index)))

def setQueryData(ident,data):
    querycache[str(ident)]=str(data)

def setQueryString(ident,namestr):
    querystring[str(ident)]=namestr
    
def setQueryRank(ident,rank):
    queryrank[str(ident)]=str(rank)
    
def setQueryDown(ident,rank):
    querydown[str(ident)]=str(rank)
    
def setQueryRel(ident,rel):
    queryrel[str(ident)]=str(rel)
    
def setQueryTemp(ident,rel):
    queryfktemp[str(ident)]=str(rel)

def getKey():
    return querycache.keys()
    

try:
    getCounter()
except TypeError,t:
    cookiecounter[1]='1025'
    
