#coding=utf-8

try:
    from nltk.tag.stanford import StanfordNERTagger
except Exception,e :
    count = 1
else:
    count = 0

if count ==0:
    def namedEntityRec(namestr):
        st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')
        #st = StanfordNERTagger('/usr/share/stanford-ner/classifiers/all.3class.distsim.crf.ser.gz','/usr/share/stanford-ner/stanford-ner.jar')
        #st = StanfordNERTagger('C:/usrs/smilelife1979/stanford-ner-2015-12-09/classifiers/english.all.3class.distsim.crf.ser.gz','C:\usrs\smilelife1979\stanford-ner-2015-12-09\stanford-ner.jar')
        #st = StanfordNERTagger('englsih.all.3class.distsim.crf.ser.gz','stanford-ner.jar')
        st.tag('Rami Eid is studying at Stony Brook University in NY'.split())
        entities_return=[]
        for num in st:
            if st[num]=='PERSON'|st[num]=='ORGANIZATION'|st[num]=='LOCATION':
                entities_return.append([str(num[0])])
        return entities_return
else :
    def namedEntityRec(namestr):
        entities_return = [u'Entity1',u'Entity2',u'Entity3']
        return entities_return

