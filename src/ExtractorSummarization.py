# -*- coding: utf-8 -*-
from goose import Goose
from gensim.summarization import summarize
#url = 'http://edition.cnn.com/2012/02/22/world/europe/uk-occupy-london/index.html?hpt=ieu_c2'
url = 'https://en.wikipedia.org/wiki/China'
#url = 'https://zh.wikipedia.org/wiki/中华人民共和国'
#url = 'http://www.chinanews.com/gj/2014/11-19/6791729.shtml'
#queryStrInput='Hong Kong'
def Extractor_Summarization(url):
    g = Goose()
    article = g.extract(url=url)
    #print article.title
    #print article.meta_description
    cleaned_text=article.cleaned_text[:]
    #print cleaned_text
    return summarize(cleaned_text)