#coding=utf-8
#载入框架 
import urllib 
import web
import sys
import StringIO
import traceback
from test import startSearch_local,adjustQuery,getStdRef
from CrawlBingData import accKey
from commonMethods import quote
from commonMethods import unquote
#from ExtractorSummarization import ExtractorSummarization

from queryData import getRelatext
from queryData import getQueryData
from queryData import setQueryData
from queryData import getQueryString
from queryData import setQueryString
from queryData import getQueryRank
from queryData import setQueryRank
from queryData import getQueryRel
from queryData import setQueryRel
from queryData import getQueryDown
from queryData import setQueryDown
from queryData import getCounter
from queryData import incCounter
from queryData import getKey
from formatfile import getCorpus as getDocs


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

maxperpage =10

def checkID():
    global count
    cookie_name = web.cookies().get("team-id")
    #print (cookie_name)
    if cookie_name is None or int(cookie_name) <= 1024:
        web.setcookie("team-id", getCounter() , expires=30000, domain=None, secure=False)
        incCounter()
        raise web.seeother('/')
    return int(cookie_name)

class Download:
    
    def GET(self):
        cookie_name = checkID()
        #print('get:')
        #print(cookie_name)
        #print('\n')
        #print(getKey())
        file = 'related work\r\n\r\n'
        refe = 'references\r\n\r\n'
        #form = web.input()
        #rec = web.input(relelinks=[])
        try:
            rel = sorted(list(getQueryRel(cookie_name)))
        except TypeError,t:
            return 'Your cookie is out of date.'
        web.header('Content-type','text/plain')  #指定返回的类型  
        web.header('Transfer-Encoding','chunked')
        web.header('Content-Disposition','attachment;filename=\
                "summary of %s.txt"'%getQueryString(cookie_name))
        #print (rec['relelinks'])
        ct = 1
        for i in rel:
            piece = getRelatext(i);
            try:
                file += '['+str(ct)+']'+'title:'+piece['title']+'\r\n'+'abstract:'+piece['description']+'\r\n'+'\r\n'
                refe += '['+str(ct)+']'+getStdRef(piece['title'])+'\r\n'
            except Exception,e:
                print('Failed to summarize doc %s'%i['url'])
                file = file+'\r\n'+i['description']+'\r\n'
            ct += 1 
        sio = StringIO.StringIO()
        sio.write(file+refe)
        return sio.getvalue()

    def POST(self):
        cookie_name = checkID()
        #print('post:')
        #print(cookie_name)
        #print('\n')
        #print(getKey())
        file = ''
        form = web.input()
        if hasattr(form,'relelinks'):
            rec = web.input(relelinks=[])
            try:
                data = getQueryData(cookie_name)
            except TypeError,t:
                return 'Your cookie is out of date.'
            for d in data:
                d['rel']=False
            for i in rec['relelinks']:
                data[int(i)]['rel']=True
            setQueryData(cookie_name,data)
            raise web.seeother(web.ctx.fullpath)
        raise web.seeother('/')
#首页类  
class Index:  
    
    def refreshEntities(self,namestr,chosen_entities,ident):
        page =1
        if chosen_entities is not None:
            thisurl = web.ctx.path+'?name='+namestr+'&entity='+quote(chosen_entities)
            #print(thisurl)
            chosen_entities = unquote(chosen_entities)
            entities_name = chosen_entities.split(' ')
            space = ' '
            try:
                rele_text = getQueryData(ident)
            except TypeError,t:
                raise web.seeother('/')
            #rele_text = buffered_answer(entities_name,page)
            #print(rele_text)
        else :
            entities_name  = []
            thisurl = web.ctx.path+'?name='+quote(namestr)
            try:
                #print '$2'
                #print getQueryRank(ident)
                rele_text = [ getRelatext(x) for x in getQueryRank(ident)]
                #print '$3'
            except TypeError,t:
                #print t
                traceback.print_exc()
                raise web.seeother('/')
        form = []
        #print(web.ctx.fullpath.find('page'))
        #print '$4'
        return render.index(namestr,form, rele_text,page,thisurl)
    
    def initQuery(self,querystr,ident=0):
        if ident == 0 :
            raise web.seeother('/')
        rank, data = startSearch_local(querystr)
        if data is None:
            data = []
        setQueryData(ident,data)
        setQueryString(ident,querystr)
        setQueryRank(ident,rank[0:maxperpage])
        setQueryRel(ident,set())
        setQueryDown(ident,set())
        
        
    def newQuery(self,rec,ident):
        if ident is None:
            raise web.seeother('/')
        try:
            predata = getQueryData(ident)
            prestr = getQueryString(ident)
            prerank = getQueryRank(ident)
            prerel = getQueryRel(ident)
            predown = getQueryDown(ident)
        except TypeError,t:
            raise web.seeother('/')
        #data = [ getRelatext(x) for x in prerank ]
        rdocs = []
        irdocs = []
        for i in range(maxperpage):
            irdocs.append(getRelatext(prerank[i]))
        for i in rec:
            irdocs[i]['rel']=True
            prerel.add(prerank[i])
        rank,data = adjustQuery(predata,None,irdocs)
        
        
        predown.update(prerank)
        rank = rank[0:maxperpage+len(predown)]
        tmprank = []
        for i in rank:
            if i not in predown:
                tmprank.append(i)
        
        
        #print tmprank
        #print predown
        #print rank
        setQueryData(ident,data)
        #setQueryString(ident,queryStr)
        setQueryRank(ident,tmprank[0:maxperpage])
        setQueryRel(ident,prerel)
        setQueryDown(ident,predown)
    
    def clearQuery(self,ident):
        global query_cache
        if query_cache.has_key(ident):
            del query_cache[ident]
    
    def GET(self,sym):
        cookie_name = checkID()
        #print(sym)
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
            elif i=='page':
                page = int(form.page)
        if namestr is None:
            raise web.seeother('/')
        return self.refreshEntities(namestr,None,cookie_name)
        
    def POST(self,sym):
        cookie_name = checkID()
        form = web.input()
        #print ('index post')
        entities_name=''
        name = None
        lastquery = ''
        chosen_entities = ''
        feedbackRec = None
        for i in form:
            #收到相关反馈信息
            if i=='requery' or i=='download':
                feedbackRec = web.input(relelinks=[])
                #print feedbackRec['relelinks']
                if i=='download':
                    raise web.seeother('/d')
                self.newQuery([] if feedbackRec['relelinks'] is None else [int(x) for x in feedbackRec['relelinks']],cookie_name)
                #print '$1'
                raise web.seeother('/s?name='+quote(form.name))
            #收到新的查询内容
            if i=='subject':
                name = form.subject
            #地址栏中的查询内容
            elif i=='name':
                lastquery = form.name
        #self.clearQuery(cookie_name)
        if name is None or name=='':
            raise web.seeother('/')
        self.initQuery(name,cookie_name)
        raise web.seeother('/s?name='+quote(name))

#定义404错误显示内容  
def notfound():  
    return web.notfound("Sorry, the page you were looking for was not found.")
      
app.notfound = notfound  
#运行  
if __name__ == '__main__':  
    app.run()