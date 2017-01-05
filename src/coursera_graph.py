#coding=utf-8
try:
    raise "sjafs"
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem.lancaster import LancasterStemmer
    from gensim import corpora, models, similarities
    from gensim.summarization import summarize
    from gensim.summarization import keywords
    import logging
except Exception,e :
    count = 1
else:
    count = 0
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

if count==0:
    def findRelevantText(namestr):
        #corpus preprocessing
        courses = [line.strip() for line in file('./courseraGraph/coursera_corpus')]
        courses_name = [course.split('\t')[0] for course in courses]
    
        #tokenize
        texts_tokenized = [[word.lower() for word in word_tokenize(document.decode('utf-8'))] for document in courses]
        #print texts_tokenized[0]
    
        #filter stopwords
        english_stopwords = stopwords.words('english')
        #print english_stopwords
        texts_filtered_stopwords = [[word for word in document if not word in english_stopwords] for document in texts_tokenized]
        #print texts_filtered_stopwords[0]
    
        #filter
        english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[',']','&','!','*','@','#','$','%']
        texts_filtered = [[word for word in document if not word in english_punctuations] for document in texts_filtered_stopwords]
        #print texts_filtered[0]
    
        #stem
        st = LancasterStemmer()
        texts_stemmed = [[st.stem(word) for word in document] for document in texts_filtered]
        #print texts_stemmed[0]
    
        #remove one-frequency words
        all_stems = sum(texts_stemmed, [])
        stems_once = set(stem for stem in set(all_stems) if all_stems.count(stem) == 1)
        texts = [[stem for stem in text if stem not in stems_once] for text in texts_stemmed]
        #print texts
    
        #文本相似度实验
        dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
    
        #assuming 10 topics
        lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=30)
        index = similarities.MatrixSimilarity(lsi[corpus])
    
        #test top-10 similar courses with Machine Learning by Andrew Ng
        ml_course = texts[210]
        ml_bow = dictionary.doc2bow(ml_course)
        ml_lsi = lsi[ml_bow]
        #print ml_lsi
    
        sims = index[ml_lsi]
        #print list(enumerate(sims))
        sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
        print sort_sims[0:11]
    
        #return
        sims_return = []
        for num in sort_sims[0:11]:
            sims_return.append([str(num[0]),courses_name[num[0]],\
                                summarize(courses[num[0]]),keywords(courses[num[0]])])
            #print 'course num:'+str(num[0])
            #print 'course name:'+courses_name[num[0]]
            #print 'course summary:'+summarize(courses[num[0]])
            #print 'course keywords:'+keywords(courses[num[0]])
            #print ''
        return sims_return
else:
    def findRelevantText(namestr):
        #return
        sims_return = []
        for num in range(0,21):
            sims_return.append(['1','2','3','4'])
            #print 'course num:'+str(num[0])
            #print 'course name:'+courses_name[num[0]]
            #print 'course summary:'+summarize(courses[num[0]])
            #print 'course keywords:'+keywords(courses[num[0]])
            #print ''
        return sims_return
