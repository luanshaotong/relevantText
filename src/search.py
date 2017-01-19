#coding=utf-8
#载入框架 
import urllib 
import web
import sys
from data_cache import buffered_answer
from data_cache import buffered_entity
from CrawlBingData import startSearch
from CrawlBingData import adjustQuery
from CrawlBingData import accKey
from commonMethods import quote
from commonMethods import unquote

#from coursera_graph import findRelevantText
#URL映射  
urls = (
        '/([se]?)','Index'
        )  
app = web.application(urls, globals())  
#模板公共变量  
t_globals = {
    'datestr': web.datestr,  
    'cookie': web.cookies,  
}  
#指定模板目录，并设定公共模板  
render = web.template.render('templates', base='base', globals=t_globals) 

 
#首页类  
class Index:  
    
    query_cache = {} 
    
    def refreshEntities(self,namestr,chosen_entities,ident):
        page =1
        all_entities = buffered_entity(namestr)
        if chosen_entities is not None:
            thisurl = web.ctx.path+'?name='+namestr+'&entity='+chosen_entities
            chosen_entities = unquote(chosen_entities)
            entities_name = chosen_entities.split(' ')
        else :
            entities_name  = all_entities
            thisurl = web.ctx.path+'?name='+namestr
        space = ' '
        if self.query_cache.has_key(ident)==False:
             self.initQuery(space.join(entities_name),ident)
        rele_text = self.query_cache[ident][1]
        #rele_text = buffered_answer(entities_name,page)
        print(rele_text)
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
        self.query_cache[ident] = [entities_name,data]
        
        
    def newQuery(self,rec,ident):
        if ident is None:
            raise web.seeother('/')
        if self.query_cache.has_key(ident)==False:
            raise web.seeother('/')
        for i in rec:
            print rec
            self.query_cache[ident][1][int(i)]['rec'] = True
        queryStr = adjustQuery(self.query_cache[ident][0],self.query_cache[ident][1])
        data , pre = startSearch(queryStr,1,accKey)
        if data is None:
            data = []
        self.query_cache[ident] = [queryStr,data]
    
    def clearQuery(self,ident):
        if self.query_cache.has_key(ident):
            del self.query_cache[ident]
        
    def checkID(self):
        cookie_name = web.cookies().get("ident")
        print(type(cookie_name))
        if cookie_name is None:
            web.setcookie("ident", 123 , expires=3000, domain=None, secure=False)
            raise web.seeother('/')
        return int(cookie_name)
    
    def GET(self,sym):
        cookie_name = self.checkID()
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
        cookie_name = self.checkID()
        print (self.query_cache[123])
        print (self.query_cache)
        form = web.input()
        print(web.data())
        entities_name=''
        name = None
        lastquery = ''
        chosen_entities = None
        feedbackRec = None
        for i in form:
            if i=='relelinks':
                feedbackRec = form.relelinks
                self.newQuery(feedbackRec,cookie_name)
                raise web.seeother(web.ctx.fullpath)
            if i=='subject':
                name = form.subject
            elif i=='entities':
                chosen_entities = web.input(entities=[])
            elif i=='page':
                print(form.page)
            elif i=='name':
                lastquery = form.name
        self.clearQuery(cookie_name)
        if name is None or name=='':
            raise web.seeother('/')
        if sym=='' or (lastquery is not None and lastquery!=name):
            raise web.seeother('/s?name='+name)
        if chosen_entities is not None:
            chosen_entities = chosen_entities.get('entities')
            for entity in chosen_entities:
                entities_name = entities_name+' '+entity
        raise web.seeother('/s?name='+quote(name)+'&entity='+quote(entities_name))

#定义404错误显示内容  
def notfound():  
    return web.notfound("Sorry, the page you were looking for was not found.")
      
app.notfound = notfound  
#运行  
if __name__ == '__main__':  
    app.run()