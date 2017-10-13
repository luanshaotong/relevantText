#coding=utf-8
#the core function is updatequery
import heapq
import sys
from time import time
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
from gensim import models,corpora
from gensim import similarities

#Pre-process text
#input is text like 'reinforcement learning a survey'
# outpot is a list like ['reinforc', 'learn', 'survey']
def preprocess(text):
    stop_words = stopwords.words('smartstopwords.txt')
    doc = [w for w in word_tokenize(text.lower() ) if not w in stop_words]  # Remove stopwords.
    doc = [w for w in doc if w.isalpha()]  # Remove numbers and punctuation.
    st = LancasterStemmer()
    # st = PorterStemmer()
    doc = [st.stem(word) for word in doc]
    return doc
###test preprocess
# doc=preprocess('reinforcement learning a survey')
# print doc

#get corpora and dictionary
#existedflag=false means to train the model and save, existedflag=True means to load from the saved model
#trainingsetpath is the path of training dateset like trainingsetpath = dir + 'abs'
#ptextsavepath is the path of processed text
#dictsavepath is the path of dictionary
def getCorpus(docs,dictionary):
    processeddocs = []
    for doc in docs:
        # Pre-process document.
        doc = preprocess(doc)
        processeddocs.append(doc)
    corpus = [dictionary.doc2bow(text) for text in processeddocs]
    return corpus


#get the topN topics of the text
#toptopicsid is a list of topic ids like [0,4,9]
def findtopNtopics(model,topics, topN,dictionary):
    # text2bow = dictionary.doc2bow(text)
    # topics=model[text2bow]
    toptopics = heapq.nlargest(topN, topics, key=lambda s: s[1])
    toptopicsid = [item[0] for item in toptopics]
    return toptopicsid

#get new query from old queryStr
#reltexts is a list of relevant texts
#irreltexts is a list of irrelevant texts
alpha = 1.0
beta = 1  # above 100 has better perforamnce,about 0.25#0.9#0.75
gamma = 0.15
def lsiupdatequery(model,qtopics, reltexts, irreltexts,topN,dictionary):
    # query=preprocess(queryStr)
    # query2bow = dictionary.doc2bow(query)
    # qtopics=model[query2bow]

    # qtoptopicsid = findtopNtopics(qtopics, topN)
    qtoptopicsid =findtopNtopics(model, qtopics, topN, dictionary)
    print 'lsiupdatequery qtoptopicsid ',qtoptopicsid
    rel_count = len(reltexts)
    irr_count = len(irreltexts)
    new_qvec = [(tid, alpha * x) for (tid, x) in qtopics]
    for reltext in reltexts:
        reltext=preprocess(reltext)
        reltext2bow = dictionary.doc2bow(reltext)
        reltopics = model[reltext2bow]
        print 'lsiupdatequery reltopics ',reltopics
        new_qvec = [(q[0],q[1] + beta / float(rel_count) * r[1]) for q, r in zip(new_qvec, reltopics)]
    for idx,irreltext in enumerate(irreltexts):
        irreltext = preprocess(irreltext)
        irreltext2bow = dictionary.doc2bow(irreltext)
        irreltopics = model[irreltext2bow]
        print 'lsiupdatequery irreltopics ', irreltopics
        # irreltoptopicsid = findtopNtopics(irreltopics, topN)
        irreltoptopicsid = findtopNtopics(model, irreltopics, topN, dictionary)
        print 'lsiupdatequery irreltoptopicsid ', irreltoptopicsid
        diffirreltopicsid = set(irreltoptopicsid).difference(set(qtoptopicsid))
        print 'lsiupdatequery diffirreltopicsid ', diffirreltopicsid
        irreltopics = [(id, p) if id in diffirreltopicsid else (id, 0) for (id, p) in irreltopics]
        print idx, 'lsiupdatequery irreltopics ', irreltopics
        new_qvec = [(q[0],q[1] - gamma / float(irr_count) * r[1]) for q, r in zip(new_qvec, irreltopics)]
    zipped=zip(*new_qvec)
    probs=map(abs,zipped[1])
    norm=max(probs)
    new_qvec = [(q[0],q[1]/norm) for q in new_qvec]
    return new_qvec

def adjustrank(topicmodel,dictionary,qtopics,docs,topN,reltexts,irreltexts):
    corpus = getCorpus(docs, dictionary)
    topicindex = similarities.MatrixSimilarity(topicmodel[corpus])
    qtopics = lsiupdatequery(topicmodel, qtopics, reltexts, irreltexts, topN, dictionary)
    sims = topicindex[qtopics]
    #sims is in the
    sims = sorted(enumerate(sims), lambda x, y: cmp(x[1], y[1]), reverse=True)
    zipped=zip(*sims)
    rerankeddocids = zipped[0]

    return rerankeddocids

###################################################
#set dictpath, modelpath
#load dictionary and topicmodel
start=time()
datadir = '../data/citeulike/'
dictpath = '../data/citeulike/trainciteulikedict'
modelpath = '../model/citeulike/trainlsiciteulikemodel'
dictionary = corpora.Dictionary.load(dictpath)
topicmodel = models.LsiModel.load(modelpath, mmap='r')
print 'load took %.2f '%(time()-start)
#transfer queryStr to topics
queryStr = 'reinforcement learning a survey'
query = preprocess(queryStr)
query2bow=dictionary.doc2bow(query)
qtopics = topicmodel[query2bow]
#docs are search results, reltexts are relevant docs according to feedback, irreltexts are irrelevant docs according to feedback
#docs are reranked according to rerankeddocids
docs = [line.strip().lower().decode('ascii', 'ignore') for line in file(datadir + 'docs.txt')]
reltexts=['a theory of the learnable']
irreltexts=['adaptive query processing a survey']
start=time()
rerankeddocids = adjustrank(topicmodel,dictionary,qtopics,docs,10,reltexts,irreltexts)
print 'adjustrank took %.2f '%(time()-start)
print rerankeddocids[0:10]