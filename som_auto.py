import serial
from datetime import datetime
import numpy as np
import threading
import protocolo
import ctypes
import time
import os
import shutil

I2S_SAMPLE_RATE = 20000

class SerialESP:
    def __init__(self, device, baudrate=115200):
        self.flagAquisitando = False
        self.ser = serial.Serial(device, baudrate)
        self.ser.flushInput()
        self.sendData("8")

        self.ser.read(1)
        self.sendACK()
        print("Comunicação inicializada com sucesso!")

    def sendData(self, data):
        self.ser.write(data.encode())
        print("Dado enviado, ACK: ")
        print(self.ser.read(1))

    def sendDataNoACK(self, data):
        self.ser.write(data.encode())


    def sendACK(self):
        self.ser.write("9".encode())
    
    def imprimeInWaiting(self):
        print(self.ser.in_waiting)

    def flushInput(self):
        self.ser.flushInput()
        print("Input flush success")

    def LeSom(self):

        print("Aquisição inicializada (Pressione Ctrl + C para parar)")
        nomeArquivoTemporarioBase = datetime.now().strftime("%Y%m%d-%H%M%S")
        pastaTemporaria = "/home/pi/gaintech/mspot-vale/data/"
        
        once = True
        soundBuffer = []
        BUFFERSIZE = I2S_SAMPLE_RATE // 2
        
        for i in range(BUFFERSIZE):
            soundBuffer.append(0)
        
        iteracoes = 5*60*2
        tamanhoBufferArquivo = iteracoes * BUFFERSIZE
        npbuffer = np.zeros(tamanhoBufferArquivo, dtype="int16")
        
        start = time.time()
        cont = 0
        cont5min = 0

        self.sendData("3")
        while True:
                antes = time.time()
                cmdlido = self.ser.read(1)
                if(cmdlido == protocolo.cmd_parar):
                    break
                bufferSize = int.from_bytes(self.ser.read(4), "little")
                print(bufferSize)
                if(bufferSize > 20000):
                    raise Exception("Erro ao ler via serial")
                soundBytesBuffer = bytearray()
                soundBytesBuffer = self.ser.read(bufferSize)
                
                for i in range(bufferSize // 2):
                    j = 2*i
                    soundBuffer[i] = ctypes.c_int16(((soundBytesBuffer[j+1] << 8) | soundBytesBuffer[j])).value

                npbuffer[cont*BUFFERSIZE:(cont+1)*BUFFERSIZE] = soundBuffer[0:BUFFERSIZE]
                print(self.ser.in_waiting)
                cont += 1
                if(cont >= iteracoes):
                    nomeArquivo = nomeArquivoTemporarioBase + "[" + str(cont5min) + "]" + ".npz"
                    caminhoArquivoTemporario = pastaTemporaria + "/" + nomeArquivo

                    if (protocolo.discoComEspacoLivre(pastaTemporaria)):
                        np.savez(caminhoArquivoTemporario, som=npbuffer.astype(np.int16))

                    cont5min += 1
                    cont = 0

                print(cont)
                print(time.time() - antes)
                if ((not self.flagAquisitando) and once):
                    once = False
                    self.paraAquisicao()
                    print("parar")

        print("Tempo aprox. de execução:")
        elapsed = time.time() - start
        print(elapsed)

        nomeArquivo = nomeArquivoTemporarioBase + "[Final].npz"
        caminhoArquivoTemporario = pastaTemporaria + "/" + nomeArquivo
        
        np.savez(caminhoArquivoTemporario, som=npbuffer.astype(np.int16))
        npbuffer = np.array([], dtype='int16')
        
        self.aguardaFimAquisicao()
     
    def iniciaAquisicao(self):
        self.flagAquisitando = True
        self.LeSom()

    def paraAquisicao(self):
        self.sendDataNoACK("4")
    
    def aguardaFimAquisicao(self):
        print("Aguardando encerramento da aquisicao")
        while self.ser.in_waiting:
            self.ser.flushInput()

    def enviaParametros(self):
        self.sendData("5")
        print(self.ser.readline())

    def encerra(self):
        self.ser.close()

    def get_input(self):
        tecla = ""
        while tecla != "4":
            tecla = input('Pressione enter para parar\n')
        self.flagAquisitando = False
        
    def moveTempFile(self, src, dst):
        shutil.move(src, dst)

def main():
    ser = SerialESP("/dev/ttyUSB0", 921600)
    try:
        ser.iniciaAquisicao()
    except Exception:
        ser.ser.write(protocolo.reset)
        time.sleep(1)
        ser.aguardaFimAquisicao()
        main()

main()
