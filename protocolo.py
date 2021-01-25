import shutil

req_param = b'0' # Requisição de parâmetros
dado_param = b'1' # Parâmetros
dado_som = b'2' # Som
cmd_init = b'3' # Comando para inicializar aquisição
cmd_parar = b'4' # Comando para parar aquisição
cmd_cfg = b'5' # Comando para Configurar

hand_shake = b'8' # Hand Shake
ack = b'9' # Acknowledgement
reset = b'P' # Reset ESP32


def discoComEspacoLivre(path_reference):
    
    disco = shutil.disk_usage(path_reference)

    if (disco.free > 500*(2**20)):
        return True
    else:
        return False
