#coding=utf-8

from coursera_graph import findRelevantText
from namedEntityRec import namedEntityRec

def buffered_answer(entitys,page):
    relevantText =  findRelevantText(entitys)
    return (len(relevantText)/10,relevantText[page*10:min(page*10+10,len(relevantText))])

def buffered_entitys(namestr):
    return namedEntityRec(namestr)