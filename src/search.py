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

query_cache = {} 
 
#首页类  
class Index:  
    
    def refreshEntities(self,namestr,choosed_entities):
        page =1
        all_entities = buffered_entity(namestr)
        if choosed_entities is not None:
            entities_name = choosed_entities.split(';')
            thisurl = web.ctx.path+'?name='+namestr+'&entity='+choosed_entities
        else :
            entities_name = all_entities
            thisurl = web.ctx.path+'?name='+namestr
        rele_text = buffered_answer(entities_name,page)
        form = []
        for entity in all_entities:
            if entities_name.count(entity)>0:
                form.append((entity,'checked ="true"'))
            else :
                form.append((entity,''))
        #print(web.ctx.fullpath.find('page'))
        return render.index(namestr,form, rele_text,page,thisurl)  
    
    def initQuery(self,entities_name,id=0):
        
    def newQuery(self,rec,id):
        if id is None:
            raise web.seeother('/')
        if query_cache.has_key(id)==False:
            raise web.seeother('/')
        queryStr = adjustQuery(query_cache[id][0],query_cache[id][1])
        data , pre = startSearch(queryStr,1,accKey)
        return data
        
    def GET(self,sym):
        cookie_name = web.cookies.get("ident")
        if cookie_name is None:
            web.setcookie("ident", 123 , expires=3000, domain=None, secure=False)
        print(sym)
        if (sym==''):
            return render.index('',[],None) 
        form  = web.input()
        namestr = None
        entities_name = None
        page = 1
        choosed_entities = None
        for i in form:
            if i=='name' :
                namestr = form.name
            elif i=='entity':
                choosed_entities = form.entity
            elif i=='page':
                page = int(form.page)
        if namestr is None:
            raise web.seeother('/')
        return refreshEntities(namestr,choosed_entities)
        
    def POST(self,sym):
        form = web.input()
        print(web.data())
        entities_name=''
        name = None
        lastquery = ''
        choosed_entities = None
        feedbackRec = None
        if hasattr(form,feedback):
            feedbackRec = form.feedback
        for i in form:
            if i=='subject':
                if sys.version_info.major==3:
                    name = urllib.parse.quote(form.subject)
                else:
                    name = urllib.quote(form.subject)
            elif i=='entities':
                choosed_entities = web.input(entities=[])
            elif i=='page':
                print(form.page)
            elif i=='name':
                if sys.version_info.major==3:
                    lastquery = urllib.parse.quote(form.name)
                else:
                    lastquery = urllib.quote(form.name)
        if feedbackRec is not None:
            return newQuery(feedbackRec,web.cookies.get("ident"))
        if name is None or name=='':
            raise web.seeother('/')
        if sym=='' or (lastquery is not None and lastquery!=name):
            print("#"+lastquery)
            print("%"+name)
            raise web.seeother('/s?name='+name)
        if choosed_entities is not None:
            choosed_entities = choosed_entities.get('entities')
            for entity in choosed_entities:
                entities_name = entities_name+';'+entity
        raise web.seeother('/s?name='+name+'&entity='+entities_name)

#定义404错误显示内容  
def notfound():  
    return web.notfound("Sorry, the page you were looking for was not found.")
      
app.notfound = notfound  
#运行  
if __name__ == '__main__':  
    app.run()