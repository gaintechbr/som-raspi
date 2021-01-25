import shutil
from os import listdir
from os.path import isfile, join
import time
from protocolo import discoComEspacoLivre

temppath = "/home/pi/gaintech/mspot-vale/data/"
database = "/media/pi/GainTech/Projeto_vale/Dados/SOM/"

while True:
    arquivosParaMover = [f for f in listdir(temppath) if isfile(join(temppath, f))]
    if(len(arquivosParaMover) > 2):
        arquivosParaMover.sort(reverse=False)
        print(arquivosParaMover)
        arquivosParaMover.pop()
        arquivosParaMover.pop()
        print(arquivosParaMover)
        if(discoComEspacoLivre(database)):
            try:
                for arquivo in arquivosParaMover:
                    print(arquivo)
                    shutil.move(temppath+arquivo, database+arquivo)
            except :
                print("HD nao conectado")
        else:
            print("HD sem espaço livre!!")
    
    time.sleep(600)
    print("ok")
