#coding=utf-8
import sys
from time import time
from metrics import computerefnums,computefeedback,computepr,computeMAP,computePK,computeRK
from model import trainw2vmodel,traindoc2vecmodel,trainmodel
from formatfile import getCorpus,queryrelevantdocs,preprocess,getabs,removepunctuation
from gensim.models.doc2vec import TaggedDocument
from gensim import similarities
startfull = time()

if __name__ == '__main__':
    #read docs, queries
    datadir = '../data/citeulike/'
    docs = [line.strip().lower().decode('ascii', 'ignore') for line in file(datadir + 'abs')]
    doctitles = [line[0:line.index(':::')] for line in docs]
    # start = time()
    # doctitles, docs = removepunctuation(datadir, 'abs')
    # print 'removepunctuation took %.2f '%(time()-start)
    # print docs[0]
    # print doctitles[0]
    # sys.exit(0)
    surveyrefs = [line.strip().lower().decode('ascii', 'ignore') for line in file(datadir + 'queryrefs')]
    rufnumlist,surveytitle,testdocs = computerefnums(surveyrefs)
    traindocs=[docs[docid] for docid in range(len(docs)) if doctitles[docid] not in testdocs]
    # surveys=surveytitle
    surveys = getabs(surveytitle, docs, doctitles)
    #cut abs
    # surveys = []
    # tags = ['this paper', 'We ', 'Our ', 'this article', 'The author']
    # for id,survey in enumerate(orgsurveys):
    #     subsurvey=findsub(survey, tags)
    #     query = surveytitle[id]+' '+subsurvey
    #     # print query
    #     surveys.append(query)
    avgrel = sum(rufnumlist) / float(len(rufnumlist))
    print 'avg relevant docs',avgrel

    method ='topic'#'word2vec'#'doc2vec'# 'topic'#'combine'#BM25'#
    existedflag = True
    datasettype = 'citeulike'  # 'nips'#
    trainingset = datadir + 'abs'
    stemflag = True
    start = time()
    processeddocs, corpus, dictionary = getCorpus(existedflag, datasettype, trainingset, datadir, stemflag)
    # processeddocs, corpus, dictionary = getCorpus(existedflag, datasettype, traindocs, datadir, stemflag)
    print 'getCorpus took %.2f seconds' % (time() - start)
    print 'traindocs ',len(traindocs)
    print 'testdocs ',len(testdocs)
    print 'doctitles ', len(doctitles)
    print 'corpus ',len(corpus)
    # 1 is doc topic update,2 is doc topic plus author topic update
    # feedback parameters
    topN=5
    fdnum=5
    loop=0

    ############train model
    modeldir = '../model/word2vec/'
    # 1 for citeulike corpus needed, 2 for google news vecsize = 300, 3 for desm, 4 for glove vecsize = 50, 100, 300
    # 5 for wiki with vecsize = 400
    w2vmethod = 1
    vecsize = 300
    trainflag = False
    # print len(processeddocs),'processeddocs[0]',processeddocs[0]
    start = time()
    if method == 'word2vec':
        model = trainw2vmodel(w2vmethod, vecsize, processeddocs, modeldir, trainflag)
    elif method == 'doc2vec':
        documents = []
        for docid, doc in enumerate(docs):
            document = TaggedDocument(doc, tags=[docid])
            documents.append(document)
        model = traindoc2vecmodel(vecsize,documents,modeldir, trainflag)
    elif method == 'topic':
        modeldir = '../model/topic/citeulike/'
        num_topics = 200
        trainflag = False
        modelflag = 'lsi'  #'lsi'#
        #1 is topic sims,2 is topic sims plus author sims
        simflag=1
        start = time()
        topicmodel = trainmodel(datasettype, trainflag, modelflag, num_topics, corpus, dictionary,modeldir)
        topicindex = similarities.MatrixSimilarity(topicmodel[corpus])
        print 'topicindex ',len(topicindex)
        print 'trainmodel took %.2f seconds' % (time() - start)
    MAP = []
    MAPlist = []
    MAPvariancelist = []
    PatKlist = []
    PatKvariancelist = []
    #for recall
    intervals = [50, 100, 150, 200]
    K = [5,10,15,20,25,30]

    Qnum=int(surveyrefs[0])
    #######for refinement and expansion
    #precisionlist[Qnum][docnum], recalllist[Qnum][docnum],resultlist[Qnum][docnum]
    precisionlist = [[] for i in range(Qnum)]
    recalllist = [[] for i in range(Qnum)]
    resultlist = [[] for i in range(Qnum)]
    fdfilters=[]
    relfdfilters = []
    lastrefend=0

    for qid, queryStr in enumerate(surveys):
        refnum = rufnumlist[qid]
        qMAP = []
        print '*********************************'
        stitle = surveytitle[qid]
        print qid,' ', stitle
        query = preprocess(queryStr)
        relevantdocs, lastrefend = queryrelevantdocs(lastrefend, refnum, surveyrefs)
        start = time()
        if method == 'word2vec' or method == 'doc2vec':
            sims = [model.n_similarity(query,doc) for doc in processeddocs]
        # sims = [model.wmdistance(query, doc) for doc in processeddocs]
        # elif method == 'doc2vec':
            # qdocument = TaggedDocument(doc, tags=[qid])
            # sims = model.n_similarity([qdocument], documents)
        # sims = [model.similarity_unseen_docs(model, query, doc) for doc in processeddocs]
        elif method == 'topic':
            query2bow = dictionary.doc2bow(query)
            qtopics = topicmodel[query2bow]
            print 'qtopics ', qtopics
            sims = topicindex[qtopics]
            print 'sims ',len(sims)
        print 'len(query) ',len(query),'init sims check took %.2f ' % (time() - start)
        sims = sorted(enumerate(sims), lambda x, y: cmp(x[1], y[1]), reverse=True)
        result = computefeedback(doctitles, sims, stitle, relevantdocs)
        precision, recall,ap, ranklist=computepr(result, refnum)
        precisionlist[qid].append(precision)
        recalllist[qid].append(recall)
        resultlist[qid].append(result)
        qMAP.append(ap)
        ###########check ap
        # checkap=computeagvp(ranklist)
        #######for refinement and expansion
        for iter in range(loop):
            reltexts=[]
            irreltexts=[]
            VRindices = []
            VNRindices = []
            count=0
            for idx in range(len(result)):
                if result[idx]['rel']==True and result[idx]['id'] not in fdfilters:
                    reltexts.append(result[idx]['content'])
                    relfdfilters.append(result[idx]['id'])
                    fdfilters.append(result[idx]['id'])
                    VRindices.append(result[idx]['id'])
                    count=count+1
                elif result[idx]['rel']==False and result[idx]['id'] not in fdfilters:
                    irreltexts.append(result[idx]['content'])
                    fdfilters.append(result[idx]['id'])
                    VNRindices.append(result[idx]['id'])
                    count = count + 1
                if count == fdnum:
                    break
            print '********'
            print qid,' query ', iter, ' loop'
            print 'reltexts RRRRRRRRRRRRRRRRRRRRRRRR ',VRindices, reltexts
            print 'irreltexts XXXXXXXXXXXXXXXXXXXXXXX ', VNRindices, irreltexts
            if len(VRindices) > 0:
                for docid in VRindices:
                    query.extend(processeddocs[docid])
            if method == 'topic':
                query2bow = dictionary.doc2bow(query)
                qtopics = topicmodel[query2bow]
                sims = topicindex[qtopics]
            elif method == 'word2vec' or method == 'doc2vec':
                start=time()
                sims = [model.n_similarity(query, doc) for doc in processeddocs]
                print 'len(query) ',len(query), ' sims check took %.2f ' % (time() - start)
            sims = sorted(enumerate(sims), lambda x, y: cmp(x[1], y[1]), reverse=True)
            result = computefeedback(doctitles, sims, stitle, relevantdocs)
            precision, recall, ap, ranklist = computepr(result, refnum)
            precisionlist[qid].append(precision)
            recalllist[qid].append(recall)
            resultlist[qid].append(result)
            qMAP.append(ap)
            ###########check ap
            # checkap = computeagvp(ranklist)
        qmaploop=round(sum(qMAP)/(loop+1),4)
        MAP.append(qmaploop)

    # print 'MAP ', MAP

    cMAP, cMAPvariance = computeMAP(resultlist, loop, rufnumlist)
    print 'computeMAP MAP ', cMAP

    precisionK =computePK(precisionlist, K)
    print 'computePK precisionK', precisionK

    recallK = computeRK(recalllist, intervals)
    print 'computeRK recallK', recallK

    print 'the whole program took %.2f seconds to run.' % (time() - startfull)