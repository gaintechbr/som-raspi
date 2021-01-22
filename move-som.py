import shutil
from os import listdir
from os.path import isfile, join
import time

temppath = "/home/pi/gaintech/mspot-vale/data/"
database = "/media/pi/Leonardo/Projeto_Vale/Dados/SOM/"

while True:
    arquivosParaMover = [f for f in listdir(temppath) if isfile(join(temppath, f))]
    arquivosParaMover.sort(reverse=False)
    print(arquivosParaMover)
    arquivosParaMover.pop()
    arquivosParaMover.pop()
    print(arquivosParaMover)
    try:
        for arquivo in arquivosParaMover:
            print(arquivo)
            shutil.move(temppath+arquivo, database+arquivo)
    except :#FileNotFoundError, PermissionError::
        print("HD nao conectado")
    time.sleep(1)
    print("ok")
