#载入框架  
import web  
from coursera_graph import findRelevantText
#URL映射  
urls = (  
        '/', 'Index',
        '/index/(\\d+)','Index'
        )  
app = web.application(urls, globals())  
#模板公共变量  
t_globals = {  
    'datestr': web.datestr,  
    'cookie': web.cookies,  
}  
#指定模板目录，并设定公共模板  
render = web.template.render('templates', base='base', globals=t_globals)  
 
analysis = ['','','']

rela_context = None

tmp_context = [['1','2','c1'],['1','2','c2']]
#首页类  
class Index:  
    def GET(self,page=0):  
        global analysis
        global rela_context
        #page = int(page)
        return render.index(analysis, rela_context,page)  
    def POST(self):
        form = web.input()
        print (web.data())
        name_str = "%s" % form.subject      #subject ,string
        global rela_context
        rela_context = findRelevantText(name_str)
        raise web.seeother('/')

#定义404错误显示内容  
def notfound():  
    return web.notfound("Sorry, the page you were looking for was not found.")  
      
app.notfound = notfound  
#运行  
if __name__ == '__main__':  
    app.run()