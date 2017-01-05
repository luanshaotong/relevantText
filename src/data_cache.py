#coding=utf-8
import urllib
import sys
from coursera_graph import findRelevantText
from namedEntityRec import get_NamedEntity

def buffered_answer(entitys,page):
    relevantText =  findRelevantText(entitys)
    return (len(relevantText)/10,relevantText[page*10:min(page*10+10,len(relevantText))])

def buffered_entitys(namestr):
    namedEntity = get_NamedEntity(namestr)
    for i in namedEntity:
        if sys.version_info.major ==3:
            i = urllib.parse.quote(i)
        else:
            i = urllib.quote(i)
    return namedEntity