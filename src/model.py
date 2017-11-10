#coding=utf-8
import re
import os
import sys
import numpy as np
from gensim import models
from gensim.models import AuthorTopicModel
from gensim.models import Word2Vec
from gensim.models import Doc2Vec
from gensim.models.doc2vec import LabeledSentence
from gensim.models import KeyedVectors

def getauthor2doc(authorfilepath):
    # Get all author names and their corresponding document IDs.
    author2doc = dict()
    doc2author = dict()
    lineno=0
    for line in open(authorfilepath):
        lineno=lineno+1
        contents = re.split(':', line)
        author_name = (contents[0]).strip().decode('ascii', 'ignore').lower()
        if author_name.count(',')<>0:
            author_name=author_name.replace(',','')
        author_name = re.sub('\s', '', author_name)
        idstr=''.join(contents[1:])
        idlist = re.split(',', idstr)
        try:
            ids = [int(c.strip()) for c in idlist]
        except:
            print lineno
            print contents[1:]
            print idstr
            print idlist
        #get author2doc
        if author_name<>'' and not author2doc.get(author_name):
        # if not author2doc.get(author_name):
            # This is a new author.
            author2doc[author_name] = []
        # Add document IDs to author.
        if author_name <> '':
            author2doc[author_name].extend([int(id) for id in ids])
            if author2doc[author_name] == []:
                print author_name, ids

        # get doc2author
        for id in ids:
            # print author_name, ids
            if not doc2author.get(id):
                # This is a new author.
                doc2author[id] = []
            # Add document IDs to author.
            doc2author[id].append(author_name)
            if doc2author[id] == []:
                print author_name, id

    return author2doc,doc2author

def trainATmodel(trainflag, corpus, num_topics, dictionary, author2doc,doc2author,datasettype,modeldir):
    if trainflag:
        model = AuthorTopicModel(corpus=corpus, num_topics=num_topics, id2word=dictionary, \
                                 author2doc=author2doc, doc2author=doc2author,chunksize=2000, passes=1, eval_every=0, \
                                 iterations=1, random_state=1)
        # Save model.
        model.save(modeldir+'ATmodel')
        # print 'new model took %.2f seconds to run.' % (time() - start)
    else:
        # Load model.
        model = AuthorTopicModel.load(modeldir+'ATmodel')
        # print 'load model took %.2f seconds to run.' % (time() - start)
    return model

#train or load topic model
#trainflag=true means to train a new model, otherwise trainflag=false means to load the saved model
#num_topics is a integer like 200
def trainmodel(datasettype,trainflag,modelflag,num_topics,corpus,dictionary,modeldir):
    # print 'trainmodel trainingsetpath ',trainingsetpath
    # load(if existed)/read and preprocessed docs
    if trainflag:
        if modelflag == 'lda':
            model = models.LdaModel(corpus, num_topics, id2word=dictionary)  # initialize an LSI transformation
            model.save(modeldir+'model.'+modelflag)
        elif modelflag == 'lsi':
            model = models.LsiModel(corpus, num_topics, id2word=dictionary)  # initialize an LSI transformation
            model.save(modeldir+'model.'+modelflag)
    else:
        if modelflag == 'lda':
            model = models.LdaModel.load(modeldir+'model.'+modelflag, mmap='r')
        elif modelflag == 'lsi':
            model = models.LsiModel.load(modeldir+'model.'+modelflag, mmap='r')
        # print 'load preprocess took %.2f seconds to run.' % (time() - start)

    return model

def trainw2vmodel(w2vmethod,vecsize,corpus,modeldir, refineflag):
    # 1-citeulike
    if w2vmethod==1:
        dir = modeldir + 'citeulike/citeulike.'
        if os.path.isfile(dir+ str(vecsize)) and refineflag==False:
            model = KeyedVectors.load(dir + str(vecsize))
        else:
            model = Word2Vec(corpus, workers=3, size=vecsize, sg=1,min_count=1)
            model.save(dir+ str(vecsize))
    elif w2vmethod==2:
        dir = modeldir + 'google/'
        if vecsize==300:
            # Train Word2Vec on all the.
            model=KeyedVectors.load_word2vec_format(dir+'GoogleNews-vectors-negative300.bin.gz',binary=True)
    elif w2vmethod==3:#unfinished
        dir = modeldir + 'desm/'
        if os.path.isfile(dir+ str(vecsize)) and refineflag==False:
            model = KeyedVectors.load(dir + str(vecsize))
        else:
            model = Word2Vec(corpus, workers=3, size=vecsize, sg=1)
            model.save(dir+ str(vecsize))
    elif w2vmethod==4:
        dir = modeldir + 'glove.6B/'
        if vecsize == 50:
            model = KeyedVectors.load_word2vec_format(dir + 'glove.6B.50d.txt', binary=False)
        elif vecsize == 100:
            model = KeyedVectors.load_word2vec_format(dir + 'glove.6B.100d.txt', binary=False)
        elif vecsize == 200:
            model = KeyedVectors.load_word2vec_format(dir + 'glove.6B.200d.txt', binary=False)
        elif vecsize == 300:
            model = KeyedVectors.load_word2vec_format(dir + 'glove.6B.300d.txt', binary=False)
    elif w2vmethod == 5:
        dir = modeldir + 'wiki/'
        model = KeyedVectors.load_word2vec_format(dir +'wiki.en.text.vector', binary=False)
        # model=Word2Vec.load(dir +'wiki.en.text.model')
    return model

def traindoc2vecmodel(vecsize,documents,modeldir, trainflag):
    dir = modeldir + 'citeulike/citeulike.'
    if os.path.isfile(dir+ str(vecsize)) and trainflag==False:
        model = Doc2Vec.load(dir + str(vecsize))
    else:
        model = Doc2Vec(documents, size=vecsize, min_count=1, workers=3)
        model.save(dir+ str(vecsize))

    return model

def doc2vecbyweight(tokens, word2vec, vecsize,doc_tfidf,dictionary,AVG=True):
    # print 'computemodel doc2vecbyweight'
    # print len(tokens), tokens
    # print len(doc_tfidf), doc_tfidf
    zipped = zip(*doc_tfidf)
    pattern_vector = np.zeros(vecsize)
    n_words = 0
    tokenslen=len(tokens)
    # mu, sigma = 0, 0.1
    if tokenslen > 1:
        for t in tokens:
            count = 0
            try:
                vector = word2vec[t.strip()]
                tid = dictionary.token2id[t.strip()]
                tindex = zipped[0].index(tid)
                weight = doc_tfidf[tindex][1]
                pattern_vector = np.add(pattern_vector,weight*vector)
                n_words += 1
            except KeyError, e:
                # print 't ',t
                # sys.exit(0)
                count = count + 1
                continue
        if AVG is True:
            try:
                pattern_vector = np.divide(pattern_vector,n_words)
            except:
                print 'n_words',n_words
        # print 'KeyError num',count
    elif tokenslen == 1:
        try:
            pattern_vector = doc_tfidf[0][1]*word2vec[tokens[0].strip()]
        except KeyError:
            pass
    return pattern_vector

def doc2vecbytopic(tokens, toptopics, topicmodel, w2vmodel,vecsize, dictionary, AVG):
    # print 'computemodel doc2vecbytopic'
    # print len(tokens), tokens
    # print len(doc_tfidf), doc_tfidf
    weights = dict()
    # print 'toptopics ',toptopics
    for topicid in toptopics:
        topic = topicmodel.show_topic(topicid[0], topn=vecsize)
        # print 'topic ',topic
        for item in topic:
            if not weights.get(item[0]):
                weights[item[0]] = 0
            freqs = topicid[1] * item[1]
            weights[item[0]] += freqs
    # print len(weights), 'weights', weights
    # sys.exit(0)
    tmp = max(weights.items(), key=lambda x: x[1])

    pattern_vector = np.zeros(vecsize)
    n_words = 0
    tokenslen=len(tokens)
    # mu, sigma = 0, 0.1
    if tokenslen > 1:
        for t in tokens:
            count = 0
            try:
                vector = w2vmodel[t.strip()]
                tid = dictionary.token2id[t.strip()]
                pattern_vector = np.add(pattern_vector,weights[tid]*vector/tmp)
                n_words += 1
            except KeyError, e:
                # print 't ',t
                # sys.exit(0)
                count = count + 1
                continue
        if AVG is True:
            try:
                pattern_vector = np.divide(pattern_vector,n_words)
            except:
                print 'n_words',n_words
        # print 'KeyError num',count
    elif tokenslen == 1:
        try:
            tid = dictionary.token2id[tokens[0].strip()]
            pattern_vector = weights[tid]*w2vmodel[tokens[0].strip()]/tmp
        except KeyError:
            pass
    return pattern_vector