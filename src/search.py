﻿#coding=utf-8
#载入框架 
import urllib 
import web
import sys
import StringIO
from data_cache import buffered_answer
from data_cache import buffered_entity
from CrawlBingData import startSearch
from CrawlBingData import adjustQuery
from CrawlBingData import accKey
from commonMethods import quote
from commonMethods import unquote
from ExtractorSummarization import ExtractorSummarization
from queryData import getQueryData
from queryData import setQueryData
from queryData import getQueryString
from queryData import setQueryString
from queryData import getCounter
from queryData import incCounter


#from coursera_graph import findRelevantText
#URL映射  
urls = (
        '/([s]?)','Index',
        '/d','Download'
        )  

app = web.application(urls, globals())  

application = app.wsgifunc()
#模板公共变量  
t_globals = {
    'datestr': web.datestr,  
    'cookie': web.cookies,  
}  
#指定模板目录，并设定公共模板  
render = web.template.render('templates', base='base', globals=t_globals) 


#query_cache = {} 

#count =10

def checkID():
    global count
    cookie_name = web.cookies().get("team-id")
    print (cookie_name)
    if cookie_name is None or int(cookie_name) <= 1024:
        web.setcookie("team-id", getCounter() , expires=3000, domain=None, secure=False)
        incCounter()
        raise web.seeother('/')
    return int(cookie_name)

class Download:
    
    def GET(self):
        return 'Please download file in search results page.'

    def POST(self):
        cookie_name = checkID()
        file = ''
        form = web.input()
        if hasattr(form,'relelinks'):
            rec = web.input(relelinks=[])
            try:
                data = getQueryData(cookie_name)
            except TypeError,t:
                return 'Your cookie is out of date.'
            web.header('Content-type','text/plain')  #指定返回的类型  
            web.header('Transfer-Encoding','chunked')
            web.header('Content-Disposition','attachment;filename=\
                    "summary of%s.txt"'%getQueryString(cookie_name))
            print (rec['relelinks'])
            for i in rec['relelinks']:
                try:
                    temp = ExtractorSummarization(data[int(i)]['url'])
                    if len(temp)<10:
                        raise 1
                    file = file+'\r\n'+temp+'\r\n'
                except Exception,e:
                    print('Failed to summarize doc %s'%i)
                    file = file+'\r\n'+data[int(i)]['description']+'\r\n'
            sio = StringIO.StringIO()
            sio.write(file)
            return sio.getvalue()
#首页类  
class Index:  
    
    def refreshEntities(self,namestr,chosen_entities,ident):
        page =1
        all_entities = buffered_entity(namestr)
        if chosen_entities is not None:
            thisurl = web.ctx.path+'?name='+namestr+'&entity='+quote(chosen_entities)
            print(thisurl)
            chosen_entities = unquote(chosen_entities)
            entities_name = chosen_entities.split(' ')
            space = ' '
            self.initQuery(space.join(entities_name),ident)
            rele_text = getQueryData(ident)
            #rele_text = buffered_answer(entities_name,page)
            print(rele_text)
        else :
            entities_name  = []
            thisurl = web.ctx.path+'?name='+namestr
            rele_text = []
        form = []
        for entity in all_entities:
            if entities_name.count(entity)>0:
                form.append((entity,'checked ="true"'))
            else :
                form.append((entity,''))
        #print(web.ctx.fullpath.find('page'))
        return render.index(namestr,form, rele_text,page,thisurl)
    
    def initQuery(self,entities_name,ident=0):
        if ident == 0 :
            raise web.seeother('/')
        data,pre = startSearch(entities_name,1,accKey)
        if data is None:
            data = []
        setQueryData(ident,data)
        setQueryString(ident,entities_name)
        
        
    def newQuery(self,rec,ident):
        if ident is None:
            raise web.seeother('/')
        try:
            predata = getQueryData(ident)
            prestr = getQueryString(ident)
        except TypeError,t:
            raise web.seeother('/')
        for i in rec:
            print rec
            predata[int(i)]['rec'] = True
        queryStr = adjustQuery(prestr,predata)
        data , pre = startSearch(queryStr,1,accKey)
        if data is None:
            data = []
        setQueryData(ident,data)
        setQueryString(ident,queryStr)
    
    def clearQuery(self,ident):
        global query_cache
        if query_cache.has_key(ident):
            del query_cache[ident]
    
    def GET(self,sym):
        cookie_name = checkID()
        print(sym)
        if (sym==''):
            return render.index('',[],None) 
        form  = web.input()
        namestr = None
        entities_name = None
        page = 1
        chosen_entities = None
        for i in form:
            if i=='name' :
                namestr = form.name
            elif i=='entity':
                chosen_entities = form.entity
            elif i=='page':
                page = int(form.page)
        if namestr is None:
            raise web.seeother('/')
        return self.refreshEntities(namestr,chosen_entities,cookie_name)
        
    def POST(self,sym):
        cookie_name = checkID()
        form = web.input()
        print ('index post')
        entities_name=''
        name = None
        lastquery = ''
        chosen_entities = ''
        feedbackRec = None
        for i in form:
            if i=='relelinks':
                feedbackRec = web.input(relelinks=[])
                self.newQuery(feedbackRec['relelinks'],cookie_name)
                raise web.seeother(web.ctx.fullpath)
            if i=='subject':
                name = form.subject
            elif i=='entities':
                chosen_entities = form.entities
            elif i=='page':
                print(form.page)
            elif i=='name':
                lastquery = form.name
        #self.clearQuery(cookie_name)
        if name is None or name=='':
            raise web.seeother('/')
        if sym=='' or (lastquery is not None and lastquery!=name):
            raise web.seeother('/s?name='+quote(name))
        
        raise web.seeother('/s?name='+quote(name)+'&entity='+quote(chosen_entities))

#定义404错误显示内容  
def notfound():  
    return web.notfound("Sorry, the page you were looking for was not found.")
      
app.notfound = notfound  
#运行  
if __name__ == '__main__':  
    app.run()