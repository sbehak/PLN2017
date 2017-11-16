import ast
import re
import nltk
from nltk.corpus import stopwords
from subprocess import Popen, PIPE, STDOUT
from nltk.metrics import *

def diccionarioElementosSubjetivos(archivoElementosSubjetivos):
    positivosRaw = open(archivoElementosSubjetivos).read()
    positivosRaw = positivosRaw.replace(u'\ufeff', '')
    positivosRaw = positivosRaw.replace('elementoSubjetivo','')
    positivosRaw = positivosRaw.strip()
    regex = re.compile(r"%.*\n", re.IGNORECASE | re.MULTILINE)
    positivosRaw = re.sub(regex,'',positivosRaw)
    regex = re.compile(r"\)(.[^\)\(]|\s[^\)\(])*\(",re.IGNORECASE | re.MULTILINE)
    positivosRaw = re.sub(regex,').(',positivosRaw)
    arregloPositivos = positivosRaw.split('.')
    #Saco punto final
    tope = len(arregloPositivos) -1
    arregloPositivos.pop(tope)
    tuplas = ()
    #Voy a tener un diccionario palabra:valor
    for tupla in arregloPositivos:
        #print(ast.literal_eval(tupla))
        tuplas = tuplas + (ast.literal_eval(tupla.strip()),)
    
    #print (tuplas)
    diccionario = dict(tuplas)
    return diccionario

def depurar_comentarios (comentarios_peliculas):
# En primera instancia se quitan los espacios en blanco al final y al principio (espacio, tab, retorno de carro, salto de linea)
# Se recorren los datos por filas
    for i in range(0,len(comentarios_peliculas)):
    # Se accede a la fila i columna 0 (es decir el valor comentario) y se lo modifica por el mismo modificado
        comentarios_peliculas.ix[i,0] = comentarios_peliculas.ix[i,0].strip(' \t\n\r')

    # Luego se quitan las etiquetas html de los comentarios
    # Se recorren los datos por filas
    for i in range(0,len(comentarios_peliculas)):
        
        # Se obtiene el largo del comentario i
        length = len(comentarios_peliculas.ix[i,0])
        new_length = 0
        
        # Expresión regular para matchear etiquetas html
        reg = r'<\/?\w+((\s+\w+(\s*=\s*(?:".*?"|\'.*?\'|[^\'">\s]+))?)+\s*|\s*)\/?>'
        
        # Se aplica la expresión regular al comentario mientras cambien los largos
        while new_length != length:
            
            # Se cambia el comentario por el mismo sin etiquetas html
            comentarios_peliculas.ix[i,0] = re.sub(reg, "", comentarios_peliculas.ix[i,0])
            new_length = len(comentarios_peliculas.ix[i,0])        
    return comentarios_peliculas

def convert_to_list(comentarios_peliculas):
    subset = comentarios_peliculas[['ComTexto','Calificación']]
    return [tuple(x) for x in subset.values]

# Funcion que dado un numero entre (1 y 5) devuelve la clasificación asociada
# En este lab si es 5 o 4 -> positivo; 3 -> neutro; 1 o 0 -> negativo
def codificarClasificacion(num):
    if(num > 3):
        return "pos"
    elif(num == 3):
        return "neu"
    else:
        return "neg"    

def tokenizar_nltk(datos):
    # Retorna una lista de tuplas. 
    # Cada tupla posee un diccionario (dict) palabra-frecuencia del comentario y la clasificación asociada
    # En otras palabras [(dict1, clasificacion1),(dict2, clasificacion2), ... ]

    listaTuplas = []

    # Se recorren los comentarios y para cada uno de ellos se tokeniza con nltk
    for i in range(0,len(datos)):
        
        # Se crea el diccionario asociado al comentario
        dic = {}
        
        # Por cada palabra retornada de la tokenizacion del comentario

        for palabra in nltk.word_tokenize(datos[i][0]):
            
            # Si la palabra está en el diccionario del comentario, se aumenta la frecuencia
            # En caso contrario se la pone en el diccionario con valor 1
            if(palabra.lower() in dic): 
                dic[palabra.lower()] = dic[palabra.lower()] + 1
            else:
                dic[palabra.lower()] = 1
                
        # Luego de tokenizado el comentario, se agrega una tupla a la lista que contendrá
        # el diccionario de frecuencias y la clasificaion asociada al comentario
        listaTuplas.insert(i,(dic,codificarClasificacion(datos[i][1])))
    return listaTuplas

def palabras_mas_frecuentes (n,datos):
    cantPalabras = 0
    palabras = {}
    for i in range(0, len(datos)):
        for palabra in nltk.word_tokenize(datos[i][0]):
            if(palabra.lower() in palabras): 
                    palabras[palabra.lower()] = palabras[palabra.lower()] + 1
            else:
                    palabras[palabra.lower()] = 1

    palabrasOrdenadasPorFrecuencia = sorted(palabras, key=palabras.get, reverse=True)
    
    if(n==-1):
        return palabrasOrdenadasPorFrecuencia
    else:
        return palabrasOrdenadasPorFrecuencia[:n]  

def filtrar(datos,filtro,not_in):
    datos_filtrados = []
    for i in range(0,len(datos)):
        #FALSE Se queda con las que pertenecen al conjunto filtro
        if(not_in):
            filt = [w for w in nltk.word_tokenize(datos[i][0]) if not w in filtro]    
        else:
            filt = [w for w in nltk.word_tokenize(datos[i][0]) if w in filtro]
        datos_filtrados.insert(i,(" ".join(filt),datos[i][1]))
    return datos_filtrados


# Funcion que dada una distribución de probabilidad de las clasificaciones
# devuelve la clasificacion que tiene mayor probabilidad
def getClasificacion(pdist):
    
    # Se inicializa la clasificacion
    clasificacion = 0;
    prob = 0
    
    # Por cada clasificacion posible, la comparo con la inicializacion
    # Me quedo con la mas grande
    for i in range(1,6):
        if( pdist.prob(i) > prob):
            clasificacion = i
            prob = pdist.prob(i)

    return clasificacion

def getTasa(clf,datos_test):
    # Se define la variable de aciertos
    aciertos = 0
    
    salidaClasificador = []
    salida = []

    # Para cada comentario del conjunto de testeo se evalua segun el algoritmo entrenado
    for comentario in datos_test:

        # Se obtiene la clasificacion del algoritmo para el comentario
        clasificacion = clf.classify(comentario[0])
        salidaClasificador.append(clasificacion)
        salida.append(comentario[1])
        
        # En caso que la clasificacion sea la correcta se aumenta el acierto
        if(clasificacion == comentario[1]):
            aciertos += 1

    cm = nltk.ConfusionMatrix(salidaClasificador, salida)
    print("Matriz de confusión:")
    print(cm)
    print("Accuracy:")
    print(accuracy(salidaClasificador, salida))    
    
    prec_pos = cm.__getitem__(("pos","pos")) / (cm.__getitem__(("pos","pos")) + cm.__getitem__(("pos","neu")) + cm.__getitem__(("pos","neg")))
    prec_neu = cm.__getitem__(("neu","neu")) / (cm.__getitem__(("neu","neu")) + cm.__getitem__(("neu","pos")) + cm.__getitem__(("neu","neg")))
    prec_neg = cm.__getitem__(("neg","neg")) / (cm.__getitem__(("neg","neg")) + cm.__getitem__(("neg","pos")) + cm.__getitem__(("neg","neu")))


    rec_pos = cm.__getitem__(("pos","pos")) / (cm.__getitem__(("pos","pos")) + cm.__getitem__(("neu","pos")) + cm.__getitem__(("neg","pos")))
    rec_neu = cm.__getitem__(("neu","neu")) / (cm.__getitem__(("neu","neu")) + cm.__getitem__(("pos","neu")) + cm.__getitem__(("neg","neu")))
    rec_neg = cm.__getitem__(("neg","neg")) / (cm.__getitem__(("neg","neg")) + cm.__getitem__(("pos","neg")) + cm.__getitem__(("neu","neg")))

    f_score_pos = "NaN"
    f_score_neu = "NaN"    
    f_score_neg = "NaN"    

    if((prec_pos + rec_pos) > 0):
        f_score_pos = 2 * prec_pos * rec_pos / (prec_pos + rec_pos)
    if((prec_neu + rec_neu) > 0):
        f_score_neu = 2 * prec_neu * rec_neu / (prec_neu + rec_neu)
    if((prec_neg + rec_neg) > 0):
        f_score_neg = 2 * prec_neg * rec_neg / (prec_neg + rec_neg)

    print("Precisión:")
    print("\tPos: " + str(prec_pos))
    print("\tNeu: " + str(prec_neu))
    print("\tNeg: " + str(prec_neg))

   
    print("Recall:")
    print("\tPos: " + str(rec_pos))
    print("\tNeu: " + str(rec_neu))
    print("\tNeg: " + str(rec_neg))

    print("F-Score:")
    print("\tPos: " + str(f_score_pos))
    print("\tNeu: " + str(f_score_neu))
    print("\tNeg: " + str(f_score_neg))

def codificarClasificacionesSubjetivos(elementos_subjetivos):
    lista = []
    for t in elementos_subjetivos:

        clasificacion = 'neg'
        if elementos_subjetivos[t] == 3:
            clasificacion = 'pos'
            
        lista.append(({t:1},clasificacion))
    
    return lista

def getPositivos(elementos_subjetivos):
    lista = []
    for t in elementos_subjetivos:

        #clasificacion = 'neg'
        if elementos_subjetivos[t] == 3:
            lista.append(t)
    
    return lista

def getNegativos(elementos_subjetivos):
    lista = []
    for t in elementos_subjetivos:

        #clasificacion = 'neg'
        if elementos_subjetivos[t] != 3:
            lista.append(t)
    
    return lista

def tokenizar_freeling(datos):
    listaTuplas = []
    
    # Retorna una lista de tuplas. 
    # Cada tupla posee un diccionario (dict) palabra-frecuencia del comentario y la clasificación asociada
    # En otras palabras [(dict1, clasificacion1),(dict2, clasificacion2), ... ]

    # Se recorren los comentarios y para cada uno de ellos se tokeniza con nltk
    for i in range(0,len(datos)):
        
        # Se crea el diccionario asociado al comentario
        dic = {}
        
        # Por cada palabra retornada de la tokenizacion del comentario
        p = Popen("%ANALYZER%/analyzer.ex -f %FREELINGSHARE%/config/es.cfg --outf splitted", shell = True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        stdout = p.communicate(input=datos[i][0].encode())[0]
        for palabra in stdout.decode().split('\r\n'):
            if(palabra == ''):
                continue
            # Si la palabra está en el diccionario del comentario, se aumenta la frecuencia
            # En caso contrario se la pone en el diccionario con valor 1
            if(palabra.lower() in dic): 
                dic[palabra.lower()] = dic[palabra.lower()] + 1
            else:
                dic[palabra.lower()] = 1
                
        # Luego de tokenizado el comentario, se agrega una tupla a la lista que contendrá
        # el diccionario de frecuencias y la clasificaion asociada al comentario
        listaTuplas.insert(i,(dic,codificarClasificacion(datos[i][1])))
    return listaTuplas

def getBestFrec (datos):
    max_val = (0,0)
    for i in range(0, len(datos)):
        if(max_val[1] < datos[i][1]):
            max_val = datos[i]
    return max_val[0]

def POS_tagging(datos):
    listaTuplas = []
    
    # Retorna una lista de tuplas. 
    # Cada tupla posee un diccionario (dict) palabra-frecuencia del comentario y la clasificación asociada
    # En otras palabras [(dict1, clasificacion1),(dict2, clasificacion2), ... ]

    # Se recorren los comentarios y para cada uno de ellos se tokeniza con nltk
    for i in range(0,len(datos)):
        # Se crea el diccionario asociado al comentario
        dic = {}
        
        # Por cada palabra retornada de la tokenizacion del comentario
        p = Popen("%ANALYZER%/analyzer.ex -f %FREELINGSHARE%/config/es.cfg", shell = True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        stdout = p.communicate(input=datos[i][0].encode())[0]
        for linea in stdout.decode().split('\r\n'):
            token = linea.split(' ')
            if len(token) < 4: 
                continue

            tag = token[2]
            palabra = token[0]
            if((tag[0:1] != 'F') and (tag[0:2] != 'RG') and (tag[0:2] != 'DP') and (tag[0:2] != 'DT') and (tag[0:2] != 'DE') 
                and (tag[0:2] != 'DA') and (tag[0:1] != 'N') and (tag[0:2] != 'RG') and (tag[0:2] != 'PP') and (tag[0:2] != 'PD')
                and (tag[0:2] != 'PX') and (tag[0:2] != 'PT') and (tag[0:2] != 'PR') and (tag[0:2] != 'PE') and (tag[0:1] != 'I')
                and (tag[0:1] != 'S') and (tag[0:1] != 'Z') and (tag[0:1] != 'W')):

                # Si la palabra está en el diccionario del comentario, se aumenta la frecuencia
                # En caso contrario se la pone en el diccionario con valor 1
                if(palabra.lower() in dic): 
                    dic[palabra.lower()] = dic[palabra.lower()] + 1
                else:
                    dic[palabra.lower()] = 1
                        
                # Luego de tokenizado el comentario, se agrega una tupla a la lista que contendrá
                # el diccionario de frecuencias y la clasificaion asociada al comentario
        listaTuplas.insert(i,(dic,codificarClasificacion(datos[i][1])))

    return listaTuplas