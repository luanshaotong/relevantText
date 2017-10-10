#coding=utf-8
#the core function is updatequery
import heapq
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
from gensim import models,corpora
from gensim.models.phrases import Phraser,Phrases

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
def getCorpus(existedflag,trainingsetpath,ptextsavepath,dictsavepath):
    if existedflag:
        processeddocs = [word_tokenize(line) for line in file(ptextsavepath)]
        dictionary = corpora.Dictionary.load(dictsavepath)
        corpus = [dictionary.doc2bow(text) for text in processeddocs]
    else:
        processeddocs = []
        docs = [line.strip() for line in file(trainingsetpath)]
        for doc in docs:
            # Pre-process document.
            doc = preprocess(doc)
            processeddocs.append(doc)
        phrases = Phrases(processeddocs, min_count=5)
        bigram = Phraser(phrases)
        with open(ptextsavepath, 'w') as docfile:
            for idx in range(len(processeddocs)):
                for token in bigram[processeddocs[idx]]:
                    if '_' in token:
                        processeddocs[idx].append(token)
                docfile.writelines(' '.join(processeddocs[idx]) + '\n')
        dictionary = corpora.Dictionary(processeddocs)
        # remove extremes (similar to the min/max df step used when creating the tf-idf matrix)
        dictionary.filter_extremes(no_below=1, no_above=0.8)
        dictionary.save(dictsavepath)
        corpus = [dictionary.doc2bow(text) for text in processeddocs]
    return corpus,dictionary

#train or load topic model
#newmodel=true means to train a new model, otherwise newmodel=false means to load the saved model
#num_topics is a integer like 200
def trainmodel(newmodel,num_topics,corpus,dictionary,modelpath):
    if newmodel:
        model = models.LsiModel(corpus, num_topics, id2word=dictionary)  # initialize an LSI transformation
        model.save(modelpath)
    else:
        # dictionary = corpora.Dictionary.load('./save/new/train'+datasettype+'dict')
        model = models.LsiModel.load(modelpath, mmap='r')
    return model

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
def updatequery(model,queryStr, reltexts, irreltexts,topN,dictionary):
    query=preprocess(queryStr)
    query2bow = dictionary.doc2bow(query)
    qtopics=model[query2bow]
    alpha = 1.0
    beta = 1  # above 100 has better perforamnce,about 0.25#0.9#0.75
    gamma = 0.15
    # qtoptopicsid = findtopNtopics(qtopics, topN)
    qtoptopicsid =findtopNtopics(model, qtopics, topN, dictionary)
    rel_count = len(reltexts)
    irr_count = len(irreltexts)
    new_qvec = [(tid, alpha * x) for (tid, x) in qtopics]
    for reltext in reltexts:
        reltext=preprocess(reltext)
        reltext2bow = dictionary.doc2bow(reltext)
        reltopics = model[reltext2bow]
        new_qvec = [(q[0],q[1] + beta / float(rel_count) * r[1]) for q, r in zip(new_qvec, reltopics)]
    for irreltext in irreltexts:
        irreltext = preprocess(irreltext)
        irreltext2bow = dictionary.doc2bow(irreltext)
        irreltopics = model[irreltext2bow]
        # irreltoptopicsid = findtopNtopics(irreltopics, topN)
        irreltoptopicsid = findtopNtopics(model, qtopics, topN, dictionary)
        diffirreltopicsid = set(irreltoptopicsid).difference(set(qtoptopicsid))
        irreltopics = [(id, p) if id in diffirreltopicsid else (id, 0) for (id, p) in irreltopics]
        new_qvec = [(q[0],q[1] - gamma / float(irr_count) * r[1]) for q, r in zip(new_qvec, irreltopics)]
    return new_qvec