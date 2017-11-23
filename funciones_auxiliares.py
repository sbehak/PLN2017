from subprocess import Popen, PIPE, STDOUT


def filtrar_corpus(corpus,filtros):
    result = []
    for i in range(0,len(corpus)):

        # Se crea el diccionario asociado al comentario
        
        diccionario = {}

        # Por cada palabra retornada de la tokenizacion del comentario
        p = Popen("C:/grondan/PLN2/FreelingWindows/bin/analyzer.bat -f C:/grondan/PLN2/FreelingWindows/data/config/es.cfg", shell = True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        try:
            stdout = p.communicate(input=corpus.loc[i,"text"].encode())[0]
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
                    if(token in dic): 
                        diccionario[token] = diccionario[token] + 1
                    else:
                        diccionario[token] = 1
            result.append({diccionario,corpus.loc[i,"humoristico"]})
        except:
            pass
    return result

