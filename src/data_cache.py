#coding=utf-8
import urllib
import sys
from coursera_graph import findRelevantText
from namedEntityRec import get_NamedEntity

def buffered_answer(entitys,page):
    relevantText =  findRelevantText(entitys)
    return (len(relevantText)/10,relevantText[page*10:min(page*10+10,len(relevantText))])

def buffered_entity(namestr):
    namedEntity = get_NamedEntity(namestr)
    for i in range(len(namedEntity)):
        namedEntity[i] = namedEntity[i].replace(' ','_')
    return namedEntity