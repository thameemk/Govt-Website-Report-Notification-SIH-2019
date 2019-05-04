#!/usr/bin/env python
# coding: utf-8

import PyPDF2
import gensim
import numpy as np
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import nltk

nltk.download('wordnet')
name = ['English-Annual Report 2016-17', 'Annual Report 2015-16-PRISMA', 'AR-NUEPA2014-15H']
l = '/Users/sreekant/Desktop/topple.pdf'
#l = 'http://www.mea.gov.in/Uploads/PublicationDocs/29788_MEA-AR-2017-18-03-02-2018.pdf'
#
pdfFileObj = open(l, 'rb')
#
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

info = pdfReader.getDocumentInfo()
date = info.get('/CreationDate')[2:6]
d = str(int(date) - 1)
date = d + " " + date
print(date)

name[0] = name[0] +"/"+ date
print(name)
#
# print(info)
#
# print(pdfReader.numPages)

# pageObj = ""
# for i in range(6):
#     s = (pdfReader.getPage(i)).extractText()
#     print(s)
#     pageObj = pageObj + " " + s
#
# print(name + " : " + date)
#
# Q = names[0] + " / " + date

import gensim
import numpy as np
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.stem.porter import *
import nltk

nltk.download('wordnet')

from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

nltk.download('stopwords')
stopword_en = stopwords.words("english")

import re
import string


# def lemmatize_stemming(text):
#   return PorterStemmer().stem( text)
def preprocessing(text):
    # result = []
    # for token in gensim.utils.simple_preprocess(text):
    #   if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
    #      result.append(lemmatize_stemming(token))
    text = re.sub(r'[^\w\s]', ' ', text)
    list = nltk.word_tokenize(text)
    result = [w.lower() for w in list if w not in stopword_en]
    # table = str.maketrans(' ', '', string.punctuation)
    # s = [w.translate(table) for w in result]
    print(result)
    return result


gen_docs = [preprocessing(name[0])] + [preprocessing(name[1])] + [preprocessing(name[2])]
print(gen_docs)

dictionary = gensim.corpora.Dictionary(gen_docs)

corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]

tf_idf = gensim.models.TfidfModel(corpus)
print(tf_idf)
s = 0
for i in corpus:
    s += len(i)
print(s)

sims = gensim.similarities.Similarity('C:/Similarity/sims', tf_idf[corpus], num_features=len(dictionary))
print(sims)
print(type(sims))

query_doc = preprocessing("annual report 2016-2017")
print(query_doc)
query_doc_bow = dictionary.doc2bow(query_doc)
print(query_doc_bow)
query_doc_tf_idf = tf_idf[query_doc_bow]
print(query_doc_tf_idf)

ar = sims[query_doc_tf_idf]
ar = ar.tolist()
print(ar)