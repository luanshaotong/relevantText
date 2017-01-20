import requests
import urllib
import sys
import codecs
import xml.etree.ElementTree as ET
import nltk
import itertools
import math
import string
from nltk.corpus import stopwords
#from ExtractorSummarization import ExtractorSummarization

rootURL = 'https://api.datamarket.azure.com/Bing/Search/v1/Web'
# To be substituted
accKey = 'gQ+gama5GAfLoQmix8AKEn5Nop24Tlu34tRapNPOImI'
# top N documents we should do calculation on
N = 10
# rocchio parameters
alpha = 2.0
beta = 0.75
gamma = 0.15

#calculate precison each iteration:
def calcPrecison(data):
	rel = 0
	for item in data:
		if item['rel']:
			rel += 1
	return float(rel) / len(data)

def startSearch(queryStr, times, accKey):
	print '========================'
	print 'Round', times
	print 'Query:', queryStr
	print '========================'
	uri = rootURL + "?Query=" + urllib.quote_plus("'" + queryStr + "'")
	result = requests.get(uri, auth=(accKey, accKey))
	# Parse result
	data = [{} for i in range(N)]
	# for test only
	tree = ET.fromstring(result.text.encode('utf-8', 'ignore'))
	#tree = etree.fromstring(result.text)
	# name space
	nsmap = {
		'base': 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Web',
		'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata',
		'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices',
		None: 'http://www.w3.org/2005/Atom'
	}
	metas = tree.findall('.//m:properties', nsmap)
	# if the result < 10, simply terminate
	if len(metas) < 10:
		return None, 0
	#set data dict values
	for i in range(N):
		title = metas[i].find('d:Title', nsmap).text
		description = metas[i].find('d:Description', nsmap).text
		url = metas[i].find('d:Url', nsmap).text
		print (title)
		# record data
		data[i]['url'] = url
		data[i]['title'] = title
		data[i]['description'] = description
		data[i]['content'] = description#ExtractorSummarization(url)
		print 'Result', i + 1
		print '['
		print ' URL:', url
		print ' Ttile:', title
		print ' Summary:', description
		print ']'
	for i in range(N):
		data[i]['rel'] = False
	#calculate precsion
	precision = calcPrecison(data)
	print '========================'
	print 'Feedback Summary'
	print 'Query:', queryStr
	print 'Precision:', precision
	return data, precision

# Adjust query - key part
def adjustQuery(queryStr, data):
	qvec, tfidf, word_set = tfidfvec(queryStr, data)
	new_queryStr = rocchio(qvec, tfidf, data, word_set, queryStr)
	return new_queryStr

#Calculate tfidf scores
def tfidfvec(query, data):
	# extract docs form raw data
	docs = [item['description'] for item in data]
	# build a list of tokenized docs
	stopwds=stopwords.words('english')
	words_list = []
	for doc in docs:
		s=[]
		for word in nltk.word_tokenize(doc):
			if((word not in stopwds) and (word not in string.punctuation)):
				s.append(word.lower())
		words_list.append(s)
	# a list of all words, with duplicates
	all_words = list(itertools.chain(*words_list))
	# a list of all words, without duplicates - for vector bases
	word_set = list(set(all_words))
	
	# construct tf vectors
	tf_vecs = [0 for i in range(N)]
	for i in range(N):
		tf_vecs[i] = [words_list[i].count(w) for w in word_set]
	# compute idf values
	idf_all_words = list(itertools.chain(*[set(doc_words) for doc_words in words_list]))
	idfs = [math.log(float(N) / idf_all_words.count(w), 10) for w in word_set]
	# compute tf-idf & normalize
	tfidf = [0 for i in range(N)]
	for i in range(N):
		tfidf[i] = [tf * idf for tf, idf in zip(tf_vecs[i], idfs)]
		nom = math.sqrt(sum(x**2 for x in tfidf[i]))
		tfidf[i] = [x / nom for x in tfidf[i]]

	# now let's work on the query vector
	qwords = [word.lower() for word in query.split()]
	# tf vector
	qvec = [qwords.count(w) for w in word_set]
	# normalize
	nom = math.sqrt(sum(x**2 for x in qvec))
	qvec = [x / nom for x in qvec]
	return qvec, tfidf, word_set

# Generate new query words
def rocchio(qvec, tfidf, data, word_set, old_query):
	# record relevant & irrelevant count
	rel_count = sum(1 for item in data if item['rel'])
	irr_count = N - rel_count
	# compute new qvec
	new_qvec = [alpha * x for x in qvec]
	for i in range(N):
		if data[i]['rel']:
			new_qvec = [q + beta / float(rel_count) * r for q, r in zip(new_qvec, tfidf[i])]
		else:
			new_qvec = [q - gamma / float(irr_count) * r for q, r in zip(new_qvec, tfidf[i])]
	# extract new query, order matters
	qwords = [word.lower() for word in old_query.split()] # may need restore later
	# top 2 largest
	sorted_qvec = [(new_qvec[i], i) for i in range(len(new_qvec))]
	sorted_qvec.sort(reverse = True)
	# number of words we can augment each time
	quota = 2
	for vec_val, index in sorted_qvec:
		if quota <= 0:
			break
		elif word_set[index] not in qwords:
			# if negative, ignore
			if vec_val <= 0:
				break
			qwords.append(word_set[index])
			quota -= 1
	qwords.sort(key = lambda w: new_qvec[word_set.index(w)], reverse = True)
	queryStr = ' '.join(qwords)
	return queryStr
