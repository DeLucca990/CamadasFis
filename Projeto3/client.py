#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 

import math
from datagrama import *
from enlace import *
import time
import numpy as np

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)

com1 = enlace(serialName)
arquivo = None
payload_size_limit = 50

def start():
    com1.enable()
    time.sleep(.2)
    com1.sendData(b'00')
    time.sleep(1)
    print("Bytes de sacrifício enviados")

def loadFile():
    global arquivo
    filename = './message.txt'
    try:
        with open(filename, "r") as file:
            arquivo = file.read()
            print("\nArquivo carregado e lido")
            file.close()
    except FileNotFoundError:
        print("Arquivo não encontrado")
        quit()

def handshake():
    handshake_head = Head('HH', 'CC', 'SS') # 'HH' (handshake) 'CC' (cliente) 'SS' (servidor).
    handshake_head.buildHead()
    handshake = Datagrama(handshake_head, '') # Cria o Datagrama com o Head e sem Payload
    com1.sendData(bytes(handshake.head.finalString + handshake.EOP, "utf-8")) # Envia o Datagrama
    print('Handshake enviado, aguardando resposta do servidor...')
    timer=0
    #print(timer)
    rxLen = com1.rx.getBufferLen()
    while not rxLen: # Aguarda a resposta do servidor
        rxLen = com1.rx.getBufferLen()
        time.sleep(1)
        timer += 1
        print(f'Tempo: {timer} segundos')
        if timer >= 5:
            raise TimeoutError # Caso o servidor não responda em 5 segundos, levanta um erro
    com1.rx.clearBuffer()


def buildPackages(): # Cria o pacote de dados que será enviado ao server
    packages = [] # Lista de pacotes
    totalPayloads = math.ceil(len(arquivo)/payload_size_limit) # Calcula o número total de pacotes
    for i in range(totalPayloads):
        head = Head('DD', 'CC', 'SS') #'DD' (dados) 'CC' (cliente) 'SS' (servidor).
        payload = ''
        for j in range(payload_size_limit):
            # Dentro deste loop, tenta adicionar elementos do arquivo ao payload. Se um IndexError ocorrer, significa que não há mais 
            # elementos no arquivo, e o loop é interrompido.
            try:
                payload += str(arquivo[i*payload_size_limit+j]) 
            except IndexError:
                break
        head.payloadData(totalPayloads, i, payload) # Adiciona os dados do payload ao Head
        head.buildHead() # Cria o Head
        datagram = Datagrama(head, payload) # Cria o Datagrama com o Head e o Payload
        packages.append(bytes(datagram.head.finalString + datagram.payload + datagram.EOP, "utf-8"))
    return packages

def main():
    try:
        handshake() # Realiza o handshake com o servidor
        print("Iniciando transmissão de mensagem")
        packages = buildPackages() # Cria os pacotes de dados
        package_id = 0 # Inicializa a para acompanhar o pacote atual.
        while package_id < len(packages):
            com1.sendData(packages[package_id]) # Envia o pacote atual
            time.sleep(0.3)
            print(f"Pacote: {package_id} / {len(packages)}")
            rxLen = 0 # Inicializa a variável que armazena o tamanho do buffer
            while not rxLen: # Aguarda a resposta do servidor
                rxLen = com1.rx.getBufferLen() # Atualiza rxLen obtendo o comprimento do buffer de recepção.
            rxBuffer, nRx = com1.getData(rxLen) # Obtém os dados recebidos do buffer de recepção e a quantidade de dados recebidos (nRx)
            decoded = rxBuffer.decode() # Decodifica os dados recebidos em UTF-8
            if decoded.startswith('88'): # Se o pacote foi recebido corretamente, o servidor envia um pacote de confirmação
                pass
            elif decoded.startswith('99'): # Se o pacote não foi recebido corretamente, o servidor envia um pacote de remandar
                package_id -= 1
            com1.rx.clearBuffer() # Limpa o buffer de recepção após processar a mensagem
            package_id += 1
        
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
    
    except TimeoutError:
        if "s" in input("Servidor inativo. Tentar novamente? S/N ").lower():
            com1.sendData(b'00')
            time.sleep(1)
            main()
        else:
            print("-------------------------")
            print("Comunicação encerrada")
            print("-------------------------")
            com1.disable()
            quit()

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    start()
    loadFile()
    main()
