import numpy as np
from scipy.io.wavfile import write

filename_in = input("Informe o nome do arquivo de origem .npz: (com extensão)")

filename_out = input("Informe o nome do arquivo de destino .wav: (com extensão)")
filename_out = "../../data/" + filename_out
buffer = np.load(filename_in)
som = buffer["som"]

write(filename_out, 20000, som.astype(np.int16))
print("Som salvo com sucesso")

