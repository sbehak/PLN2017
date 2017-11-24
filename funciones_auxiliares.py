from subprocess import Popen, PIPE, STDOUT
import datetime

def filtrar_corpus(corpus,filtros):
    result = []
    palabras = ""
    finTweet = "sringQueRepresentaFinTweetGrupo13PLNFING2017"
    print ("previo concatenar tweets")
    for i in range(0,len(corpus)):
        try:
            palabras+= corpus.loc[i,"text"].encode()
            palabras+= finTweet
        except:
            pass
    print ("fin concatenar tweets")
    # Se crea el diccionario asociado al comentario
    
    diccionario = {}

    # Por cada palabra retornada de la tokenizacion del comentario
    print ("previo open: ")
    p = Popen("C:/grondan/PLN2/FreelingWindows/bin/analyzer.bat -f C:/grondan/PLN2/FreelingWindows/data/config/es.cfg", shell = True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    print ("post open")
    try:
        stdout = p.communicate(input=palabras)[0]
        print ("post comunicate POSTA")
        for palabra in stdout.decode().split('\r\n'):
            #print(palabra)
            if(palabra == ''):
                continue
            tokens = palabra.split(' ')
            token = tokens[1]
            tag = tokens[2]
            result = []
            flag = True
            for filtro in filtros:
                tag = tag[0:len(filtro)]
                if (tag == filtro):
                    flag = False
                    break
            if flag:
                if(token in diccionario): 
                    diccionario[token] = diccionario[token] + 1
                else:
                    diccionario[token] = 1
        result.append({diccionario,corpus.loc[i,"humoristico"]})
    except:
        pass
    return result

