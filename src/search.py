#coding=utf-8
#载入框架 
import urllib 
import web
import sys
from data_cache import buffered_answer
from data_cache import buffered_entitys
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
    def GET(self,sym):
        print(sym)
        if (sym==''):
            return render.index('',[],None) 
        form  = web.input()
        namestr = None
        entitys_name = None
        page = 1
        choosed_entitys = None
        for i in form:
            if i=='name' :
                namestr = form.name
            elif i=='entity':
                choosed_entitys = form.entity
            elif i=='page':
                page = int(form.page)
        if namestr is None:
            raise web.seeother('/')
        all_entitys = buffered_entitys(namestr)
        if choosed_entitys is not None:
            entitys_name = choosed_entitys.split(';')
            thisurl = web.ctx.path+'?name='+namestr+'&entity='+choosed_entitys
        else :
            entitys_name = all_entitys
            thisurl = web.ctx.path+'?name='+namestr
        rele_text = buffered_answer(entitys_name,page)
        form = []
        for entity in all_entitys:
            if entitys_name.count(entity)>0:
                form.append((entity,'checked ="true"'))
            else :
                form.append((entity,''))
        #print(web.ctx.fullpath.find('page'))
        return render.index(namestr,form, rele_text,page,thisurl)  
    def POST(self,sym):
        form = web.input()
        print(web.data())
        entitys_name=''
        name = None
        lastquery = ''
        choosed_entitys = None
        for i in form:
            if i=='subject':
                if sys.version_info.major==3:
                    name = urllib.parse.quote(form.subject)
                else:
                    name = urllib.quote(form.subject)
            elif i=='entitys':
                choosed_entitys = web.input(entitys=[])
            elif i=='page':
                print(form.page)
            elif i=='name':
                if sys.version_info.major==3:
                    lastquery = urllib.parse.quote(form.name)
                else:
                    lastquery = urllib.quote(form.name)
        if name is None or name=='':
            raise web.seeother('/')
        if sym=='' or (lastquery is not None and lastquery!=name):
            print("#"+lastquery)
            print("%"+name)
            raise web.seeother('/s?name='+name)
        if choosed_entitys is not None:
            choosed_entitys = choosed_entitys.get('entitys')
            for entity in choosed_entitys:
                entitys_name = entitys_name+';'+entity
        raise web.seeother('/s?name='+name+'&entity='+entitys_name)

#定义404错误显示内容  
def notfound():  
    return web.notfound("Sorry, the page you were looking for was not found.")
      
app.notfound = notfound  
#运行  
if __name__ == '__main__':  
    app.run()