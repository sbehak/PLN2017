from subprocess import Popen, PIPE, STDOUT
import datetime
import traceback as tb
import os
import statistics
import math
import pandas
import csv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cross_validation import train_test_split
import re
#import freeling
from pylab import *
import numpy as np
from nltk.corpus import stopwords
import IPython.display as disp
import os
import nltk
from nltk.metrics.scores import *


def filtrar_corpus(corpus, filtros, train, lemma = False, usuario = False, with_tag = False, mediana = False):
    result = []
    palabras = ""
    finTweetH = "13grupoPLN"
    finTweetNH = "13grupoIPLN"
    
    for index, tweet in corpus.iterrows():
        palabras+= tweet["text"]
        palabras+= ". "
        if(tweet["humoristico"]):
            palabras+= finTweetH
        else:
            palabras+= finTweetNH
        palabras+= ". "
        
    #os.environ['FREELINGWINDOWS'] = 'C:/grondan/PLN2/FreelingWindows'
    dir = os.environ['FREELINGWINDOWS']
    if dir != None:
        cfg = dir+ '/data/config/es.cfg'
        analyzer = dir+ '/bin/analyzer.bat'
        p = Popen(str(analyzer)+ " -f " + str(cfg), shell = True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        stdout = p.communicate(input=palabras.encode())[0]
        iterator = -1
        tweets = stdout.decode().split('\r\n')
        for index, row in corpus.iterrows():
            iterator += 1
            tokens = tweets[iterator].split(' ')
            diccionario = {}
            while (tokens[0] != finTweetH and tokens[0] != finTweetNH):
                if(tokens[0] != ''):
                    if(lemma):
                        token = tokens[1]
                    else:
                        token = tokens[0]
                    tag = tokens[2]
                    flag = True
                    for filtro in filtros:
                        tag_aux = tag[0:len(filtro)]
                        if (tag_aux == filtro):
                            flag = False
                            break
                    if flag:
                        if(token in diccionario):
                            diccionario[token] += 1
                        else:
                            diccionario[token] = 1
                        if(with_tag):
                            if(tag in diccionario):
                                diccionario[tag] += 1
                            else:
                                diccionario[tag] = 1
                tokens = tweets[iterator].split(' ')
                iterator += 1
            if(usuario):
                hola = row["account_id"]
                diccionario[hola] = 1
            if(train):
                if(mediana):
                    result.append((diccionario, row["mediana"]))
                else:
                    result.append((diccionario, tokens[0] == finTweetH))
            else:
                result.append(diccionario)
    else:
        print ("debe indicar la ruta donde tiene instalado freeling")
    return result


def preprocesar_corpus(corpus):
    corpus["humoristico"] = [False]*len(corpus)
    corpus_filtrado = pandas.DataFrame(columns = ['text', 'account_id', 'n', '1', '2', '3', '4', '5', 'humoristico', 'cantCalificaciones', 'mediana'])
    #corpus_filtrado = corpus[corpus.n + corpus.columns[4] + corpus.columns[5] + corpus.columns[6] + corpus.columns[7] + corpus.columns[8] >= 3]
    total = 0
    for i in range(0, len(corpus)):
        contador = corpus.loc[i, "cantCalificaciones"]
        #eliminamos los hashtags
        corpus.loc[i, "text"] = re.sub(r"#\S+\s*", "", corpus.loc[i, "text"])
        #definimos si un tweet es humoristico o no segun los votos
        if(contador/2 >= corpus.loc[i, "n"]):
            corpus.loc[i, "humoristico"] = True
        #calculo mediana
        califications= []
        califications += [0]* corpus.loc[i, "n"]
        califications += [1]* corpus.loc[i, "1"]
        califications += [2]* corpus.loc[i, "2"]
        califications += [3]* corpus.loc[i, "3"]
        califications += [4]* corpus.loc[i, "4"]
        califications += [5]* corpus.loc[i, "5"]
        mediana = statistics.median(califications)
        if (trunc(mediana) < mediana):
            mediana = trunc(mediana) +1
        corpus.loc[i,"mediana"] = mediana
        #filtramos los tweets que tienen menos de 3 votos
        if contador >= 3:
            corpus_filtrado.loc[total] = [corpus.loc[i, "text"], corpus.loc[i, "account_id"], corpus.loc[i, "n"], corpus.loc[i, "1"], corpus.loc[i, "2"], corpus.loc[i, "3"], corpus.loc[i, "4"], corpus.loc[i, "5"], corpus.loc[i, "humoristico"], corpus.loc[i, "cantCalificaciones"],corpus.loc[i,"mediana"]]
            total += 1

    #columna 3 -> n, 4 -> 1, 5 -> 2, 6 -> 3, 7 -> 4, 8 -> 5

    disp.display(corpus_filtrado.loc[0:10, :])
    print ("Cantidad de tweets que quedan en el corpus luego del filtrado: " + str(len(corpus_filtrado)))
    return corpus_filtrado

def clasificar_corpus(corpus_training, corpus_testing, esMediana: False):
    corpus_pos_tagging = filtrar_corpus(corpus_training, ["P", "S", "Z", "D"], True, True, True, True, esMediana)
    clf = nltk.classify.MaxentClassifier.train(corpus_pos_tagging, max_iter=8,trace=0)
    corpus_test_tokenizado = filtrar_corpus(corpus_testing, ["P", "S", "Z", "D"], False, True, True, True)
    clasificacionCLF = []
    clasificacionOficial = []
    for tweet in corpus_test_tokenizado:
        #Clasificamos los tweets del corpus de test
        clasificacion = clf.classify(tweet)
        clasificacionCLF.append(clasificacion)
    return clasificacionCLF
      