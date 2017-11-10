#coding=utf-8
import sys
from time import time
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
from gensim import corpora
from gensim.models.phrases import Phraser,Phrases
from gensim import similarities
import string
# datadir = '../data/citeulike/'
#####to combine titles and abs to one file with title+abs
def combinetitleabsfile(titlefile,absfile,newfile):
    doctitles = [line.strip().lower().decode('ascii', 'ignore') for line in file(titlefile)]
    docs = [line.strip().lower().decode('ascii', 'ignore') for line in file(absfile)]
    if len(doctitles)<>len(docs):
        print 'combinetitleabsfile len(doctitles)<>len(docs)'
        sys.exit(0)
    linenos=len(doctitles)
    with open(newfile,'w') as newabsfile:
        for lineno in range(linenos-1):
            line=doctitles[lineno]+':::'+docs[lineno]
            newabsfile.writelines(''.join(line)+'\n')
        line = doctitles[linenos-1] + ':::' + docs[linenos-1]
        newabsfile.writelines(''.join(line) )

####test combinetitleabsfile
# titlefile=dir + 'titles'
# absfile=dir + 'abs'
# newfile=dir + 'newabsfile'
# start=time()
# combinetitleabsfile(titlefile,absfile,newfile)
# print 'combinetitleabsfile took %.2f seconds'%(time()-start)
def removepunctuation(datadir,filename):
    print datadir+filename
    docs = [line.strip().lower().decode('ascii', 'ignore') for line in file(datadir + filename)]
    doctitles = [line[0:line.index(':::')] for line in docs]
    identity = string.maketrans("","")
    docs = [line.translate(string.punctuation) for line in docs]
    doctitles = [line.translate(string.punctuation) for line in doctitles]
    return doctitles,docs

def preprocess(doc):
    stop_words = stopwords.words('smartstopwords.txt')
    start = time()
    doc = [w for w in word_tokenize(doc.lower() ) if not w in stop_words]  # Remove stopwords.
    doc = [w for w in doc if w.isalpha()]  # Remove numbers and punctuation.
    st = LancasterStemmer()
    # st = PorterStemmer()
    doc = [st.stem(word) for word in doc]
    return doc

def preprocessnostem(doc):
    stop_words = stopwords.words('smartstopwords.txt')
    doc = doc.lower()  # Lower the text.
    doc = word_tokenize(doc)  # Split into words.
    doc = [w for w in doc if not w in stop_words]  # Remove stopwords.
    doc = [w for w in doc if w.isalpha()]  # Remove numbers and punctuation.
    return doc
#test
# text = 'semantic integration a survey of ontology based approaches,semantic integration is an active area of \
# research in several disciplines, such as databases, informationintegration, and ontologies this paper provides \
# a brief survey of the approaches to semantic integration developed by researchers in the ontology community we \
# focus on the approaches that differentiate the ontology research from other related areas the goal of the paper \
# is to provide a reader who may not be very familiar with ontology research with introduction to major themes in \
# this research and with pointers to different research projects we discuss techniques for finding correspondences \
# between ontologies, declarative ways of representing these correspondences, and use of these correspondences in \
# various semantic integration tasks'
#
# doc = preprocessnostem(text)
# docset=set(doc)
# print len(docset),' '
# for item in docset:
#     print item

def getCorpus(existedflag,datasettype,trainingset,datadir,stemflag):
    if existedflag:
        processeddocs = [word_tokenize(line) for line in file(datadir+'preprocess.train')]
        dictionary = corpora.Dictionary.load(datadir+'dict.train')
        corpus = [dictionary.doc2bow(text) for text in processeddocs]
    else:
        processeddocs = []
        if datasettype == 'citeulike':
            if isinstance(trainingset,str):
                docs = [line.strip() for line in file(trainingset)]
            elif isinstance(trainingset,list):
                docs=trainingset
            start=time()
            for doc in docs:
                # Pre-process document.
                if stemflag:
                    doc = preprocess(doc)
                else:
                    doc = preprocessnostem(doc)
                # Add to corpus for training Word2Vec.
                processeddocs.append(doc)
            phrases = Phrases(processeddocs, min_count=5)
            bigram = Phraser(phrases)
            with open(datadir+'preprocess.train', 'w') as docfile:
                for idx in range(len(processeddocs)):
                    for token in bigram[processeddocs[idx]]:
                        if '_' in token:
                            # print 'trainmodel prhase token ',token
                            # Token is a bigram, add to document.
                            processeddocs[idx].append(token)
                    docfile.writelines(' '.join(processeddocs[idx]) + '\n')
                # print 'new trainpreprocess took %.2f seconds to run.' % (time() - start)

        start = time()
        dictionary = corpora.Dictionary(processeddocs)
        # remove extremes (similar to the min/max df step used when creating the tf-idf matrix)
        dictionary.filter_extremes(no_below=1, no_above=0.8)
        dictionary.save(datadir+'dict.train')
        corpus = [dictionary.doc2bow(text) for text in processeddocs]
    return processeddocs,corpus,dictionary
#test isinstance
# trainingset = datadir + 'abs'
# trainingset = [line.lower().strip().decode('ascii', 'ignore') for line in file(datadir + 'queryrefs')]
# if isinstance(trainingset, str):
#     docs = [line.strip() for line in file(trainingset)]
# elif isinstance(trainingset, list):
#     docs = trainingset
# print docs[0:5]

def processtestdoc(newpreprocess,testdocs,datadir,modelflag,datasettype,dictionary,topicmodel,stemflag):
    processed_testdocs = []  # Documents to train word2vec on
    if newpreprocess:
        start = time()
        with open(datadir+'preprocess.test', 'w') as testfile:
            start = time()
            for doc in testdocs:
                # Pre-process document.
                if stemflag:
                    doc = preprocess(doc)
                else:
                    doc = preprocessnostem(doc)
                # Add to corpus for training Word2Vec.
                processed_testdocs.append(doc)
            print 'new preprocess took %.2f seconds to run.' % (time() - start)
            phrases = Phrases(processed_testdocs, min_count=5)
            bigram = Phraser(phrases)
            for idx in range(len(processed_testdocs)):
                for token in bigram[processed_testdocs[idx]]:
                    if '_' in token:
                        # Token is a bigram, add to document.
                        processed_testdocs[idx].append(token)
                testfile.writelines(' '.join(processed_testdocs[idx]) + '\n')
        testcorpus = [dictionary.doc2bow(text) for text in processed_testdocs]
        corpus2modelspace = topicmodel[testcorpus]
        topicindex = similarities.MatrixSimilarity(corpus2modelspace)
        topicindex.save(datadir+'index.test')
    # print 'new dict took %.2f seconds to run.' % (time() - start)
    else:
        #     start = time()
        processed_docs = [word_tokenize(line) for line in file(dir+'preprocess.test')]
        testcorpus = [dictionary.doc2bow(text) for text in processed_docs]
        #     tfidf = models.TfidfModel.load('./save/new/citeuliketesttfidf_model')
        corpus2modelspace = topicmodel[testcorpus]
        topicindex = similarities.MatrixSimilarity(corpus2modelspace)
        topicindex.save(datadir+'index.test')
    return processed_testdocs

def queryrelevantdocs(lastrefend,refnum,queryanswers):
    # relevant articles:
    refend = lastrefend
    if refend == 0:
        surveyline = refend + 2
    else:
        surveyline = refend + 1
    refbegin = surveyline + 1
    refend = surveyline + int(refnum) + 1
    relevantdocs = queryanswers[refbegin:refend]
    relevantdocs = [doc.strip().lower().decode('ascii', 'ignore') for doc in relevantdocs]
    return relevantdocs,refend

def getabs(titles,docs,doctitles):
    abs = []
    for title in titles:
        if title in doctitles:
            idx = doctitles.index(title)
            abs.append(docs[idx])
    # abs = [abs for abs in docs for title in titles if title in doctitles]
    # print 'len(abs) with doctitles ',len(abs),abs[0:2]
    # abs = [abs for abs in docs for title in titles if title in docs]
    # print 'len(abs) with docs ', len(abs)
    return abs
#test getabs
# from computemetrics import computerefnums
# datadir = '../data/citeulike/'
# docs = [line.strip().lower().decode('ascii', 'ignore') for line in file(datadir + 'abs')]
# surveyrefs = [line.lower().strip().decode('ascii', 'ignore') for line in file(datadir + 'queryrefs1')]
# rufnumlist,surveytitle,testdocs = computerefnums(surveyrefs)
# surveyabs = getabs(surveytitle,docs)
# print surveyabs

def findsub(doc,tags):
    doc = doc.lower()  # Lower the text.
    # print doc
    # tags = tags.lower()  # Lower the text.
    index=len(doc)
    if len(tags)==0:
        subdoc = doc
    else:
        for tag in tags:
            # print tag
            # print 'this paper'
            tmp=doc.find(tag.lower())
            # tmp = doc.find('this paper')
            if tmp<index and tmp<>-1:
                index=tmp
                # break
        # print index
        if index<len(doc):
            subdoc=doc[index:]
        else:
            subdoc=doc
    return subdoc

datadir = './'

method ='topic'
existedflag = True
datasettype = 'nips'#'citeulike'  # 'nips'#
trainingset = datadir + 'abs'
stemflag = True

processeddocs, corpus, dictionary = getCorpus(\
                                              existedflag,\
                                              datasettype,\
                                              None, datadir, stemflag)


