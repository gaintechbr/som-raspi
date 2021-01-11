
import serial
from datetime import datetime
import numpy as np
import threading
import protocolo
from scipy.io.wavfile import write
import ctypes
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
        basefilename = datetime.now().strftime("%Y%m%d-%H%M%S")
        once = True
        soundBuffer = []
        BUFFERSIZE = I2S_SAMPLE_RATE // 4
        
        for i in range(BUFFERSIZE):
            soundBuffer.append(0)
        
        npbuffer = np.array([], dtype='int16')
        cont = 0
        contMinutos = 0
        while True:
                cont += 1
                cmdlido = self.ser.read(1)
                print(cmdlido)
                if(cmdlido == protocolo.cmd_parar):
                    break
                self.ser.readline()
                bufferSize = int.from_bytes(self.ser.read(4), "little")
                print(bufferSize)
                soundBytesBuffer = bytearray()
                soundBytesBuffer = self.ser.read(bufferSize)
                
                for i in range(bufferSize//2):
                    soundBuffer[i] = ctypes.c_int16(((soundBytesBuffer[i] << 8) | soundBytesBuffer[i+1])).value

                npbuffer = np.append(npbuffer, np.array(soundBuffer))
                print("Buffer de som lido e salvo com sucesso.")
                if ((not self.flagAquisitando) and once):
                    once = False
                    self.paraAquisicao()
                    print("parar")
    # if cont >= 240:
        # contMinutos += 1
        filename = basefilename + "[" + str(contMinutos)  + "]"+ ".wav"
        # np.savez_compressed(filename, som=npbuffer)
        write(filename, I2S_SAMPLE_RATE, npbuffer.astype(np.int16))
        npbuffer = np.array([], dtype='int16')
        # cont = 0
        self.aguardaFimAquisicao()
     
    def iniciaAquisicao(self):
        self.sendData("3")
        self.flagAquisitando = True
        i = threading.Thread(target=self.get_input)
        i.start()
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
    while True:
        entrada = input('\n\nInsira uma opção:\n3: Iniciar Aquisicao\n5: Enviar parametros\n6: Imprime InWaiting\n7: flush input\n0: Sair)')
        
        if entrada == "3":
            ser.iniciaAquisicao()
        elif entrada == "5":
            ser.enviaParametros()
        elif entrada == "6":
            ser.imprimeInWaiting()
            print(protocolo.cmd_parar)
        elif entrada == "7":
            ser.flushInput()
        elif entrada == 'c':
            loaded = np.load('20210110-213632[2].npz')
            print(loaded.files)
            som = loaded['som']

            print(len(som))
            # print(som[0])
            # print(som[1])
            # print(som[2])
            # print(loaded[3])
            # print(loaded[4])
            # print(loaded[5])
            # print(loaded[6])

        elif entrada == "0":
            ser.sendDataNoACK("P")
            ser.encerra()
            break
        else:
            print("Entrada inválida!")

main()