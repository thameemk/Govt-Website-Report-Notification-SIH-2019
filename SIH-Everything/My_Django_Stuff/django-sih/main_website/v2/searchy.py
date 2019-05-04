#!/usr/bin/env python
# coding: utf-8

import PyPDF2
import gensim
import numpy as np
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
import nltk

nltk.download('punkt')
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *

from urllib.request import urlretrieve
import os
import base64


def startSimilarity(n, names, k):
    # n = 0  # number in the db

    print(n)
    print(names)
    print(k)
    l = []

    for i in range(n):
        file_path = str(names[i])
        urlretrieve(k[i], file_path)

    l = names

    names = [name.split("/")[-1] for name in names]

    def dateRead(l, n):
        pdfReader = PyPDF2.PdfFileReader(l)
        info = pdfReader.getDocumentInfo()

        date = info.get('/CreationDate')[2:6]
        d = str(int(date) - 1)
        date = d + " " + date

        Q = names[n] + " / " + date
        return Q

    print(l)
    print(k)

    # for i in range(len(database)):
    for i in range(n):
        names[i] = dateRead(l[i], i)

    print(names)

    from nltk.corpus import stopwords
    from nltk.tokenize import RegexpTokenizer

    nltk.download('stopwords')
    stopword_en = stopwords.words("english")

    import re
    import string

    def preprocessing(text):
        text = re.sub(r'[^\w\s]', ' ', text)
        list = nltk.word_tokenize(text)
        result = [w.lower() for w in list if w not in stopword_en]
        return result

    gen_docs = []
    for i in range(len(names)):
        gen_docs = gen_docs + [preprocessing(names[i])]

    dictionary = gensim.corpora.Dictionary(gen_docs)
    corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]
    tf_idf = gensim.models.TfidfModel(corpus)

    s = 0
    for i in corpus:
        s += len(i)

    sims = gensim.similarities.Similarity('', tf_idf[corpus],
                                          num_features=len(dictionary))

    # search query
    query_doc = preprocessing("2016")
    query_doc_bow = dictionary.doc2bow(query_doc)

    query_doc_tf_idf = tf_idf[query_doc_bow]

    ar = sims[query_doc_tf_idf]
    ar = ar.tolist()
    print(ar)


    results = dict(zip(l, ar))
    print("Its coming!!!!!!")
    print(results)
