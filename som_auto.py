
import serial
from datetime import datetime
import numpy as np
import threading
import protocolo
from scipy.io.wavfile import write
import ctypes
import time
import os
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
        dataEHoraDoInicio = datetime.now().strftime("%Y%m%d-%H%M%S")
        basefolder = "/home/pi/gaintech/mspot-vale/data/" + dataEHoraDoInicio
        os.mkdir(basefolder)
        basefilename = basefolder + "/" + dataEHoraDoInicio
        once = True
        soundBuffer = []
        BUFFERSIZE = I2S_SAMPLE_RATE // 2
        
        for i in range(BUFFERSIZE):
            soundBuffer.append(0)
        
        npbuffer = np.array([], dtype='int16')
        start = time.time()
        cont = 0
        cont5min = 0
        while True:
                antes = time.time()
                cmdlido = self.ser.read(1)
                if(cmdlido == protocolo.cmd_parar):
                    break
                # print(self.ser.readline())
                bufferSize = int.from_bytes(self.ser.read(4), "little")
                print(bufferSize)
                soundBytesBuffer = bytearray()
                soundBytesBuffer = self.ser.read(bufferSize)
                
                for i in range(bufferSize // 2):
                    j = 2*i
                    soundBuffer[i] = ctypes.c_int16(((soundBytesBuffer[j+1] << 8) | soundBytesBuffer[j])).value

                npbuffer = np.append(npbuffer, np.array(soundBuffer))
                print(self.ser.in_waiting)
                # print("Buffer de som lido e salvo com sucesso.")
                cont += 1
                if(cont >= 5*60*2):
                    filename = basefilename + "[" + str(cont5min) + "]" + ".npz"
                    np.savez(filename, som=npbuffer.astype(np.int16))
                    # filename = basefilename + "[" + str(cont5min) + "]" + ".wav"
                    # write(filename, I2S_SAMPLE_RATE, npbuffer.astype(np.int16))
                    npbuffer = np.array([], dtype='int16')
                    cont5min += 1
                    cont = 0

                print(len(npbuffer))
                print(time.time() - antes)
                if ((not self.flagAquisitando) and once):
                    once = False
                    self.paraAquisicao()
                    print("parar")
        
        print("Tempo aprox. de execução:")
        elapsed = time.time() - start
        print(elapsed)
        # print(len(npbuffer)/I2S_SAMPLE_RATE)
        filename = basefilename + "[Final].npz"
        np.savez(filename, som=npbuffer.astype(np.int16))
        # filename = basefilename + "[Final].wav"
        # write(filename, I2S_SAMPLE_RATE, npbuffer.astype(np.int16))
        npbuffer = np.array([], dtype='int16')
        self.aguardaFimAquisicao()
     
    def iniciaAquisicao(self):
        self.sendData("3")
        self.flagAquisitando = True
        # i = threading.Thread(target=self.get_input)
        # i.start()
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
        
    

def main():
    ser = SerialESP("/dev/ttyUSB0", 921600)
    ser.iniciaAquisicao()
    # while True:
    #     entrada = input('\n\nInsira uma opção:\n3: Iniciar Aquisicao\n5: Enviar parametros\n6: Imprime InWaiting\n7: flush input\n0: Sair)')
        
    #     if entrada == "3":
    #         ser.iniciaAquisicao()
    #     elif entrada == "5":
    #         ser.enviaParametros()
    #     elif entrada == "6":
    #         ser.imprimeInWaiting()
    #         print(protocolo.cmd_parar)
    #     elif entrada == "7":
    #         ser.flushInput()
    #     elif entrada == "0":
    #         ser.sendDataNoACK("P")
    #         ser.encerra()
    #         break
    #     else:
    #         print("Entrada inválida!")

main()