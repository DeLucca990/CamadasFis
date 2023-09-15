#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 

import math
from enlace import *
import time
import numpy as np
import os
from datetime import datetime

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)
com1 = enlace(serialName)

class Server:
    def __init__(self, serialName):
        self.serialName = serialName
        self.logs = ''

    def startServer(self):
        self.serverCom = enlace(self.serialName)
        self.serverCom.enable()
    
    def closeServer(self):
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        self.serverCom.disable()
        exit()
    
    def receiveData(self, n):
        data = self.serverCom.getData(n)
        return data

    def sendData(self, data):
        self.serverCom.sendData(data)

    # Recebe o handshake do client
    def receiveHandshake(self, n):
        pack, lenpack = self.serverCom.getData(n)
        self.createLog(pack, 'recebimento') # Cria o log
        pack = list(pack)
        pack = list(map(int, pack)) # Transforma os dados em inteiros
        pack[0] = 2 # Muda o tipo da mensagem para 2 (handshake)
        responseHandshake = b''
        for i in pack:
            responseHandshake += (i).to_bytes(1, byteorder='big')    
        return responseHandshake, lenpack
    
    def splitHead(self, data):
        head = data[:10]
        h0 = head[0] # Tipo da Mensagem
        h1 = head[1] # Se tipo for 1: número do servidor. Qualquer outro tipo: livre 
        h2 = head[2] # Livre
        h3 = head[3] # Numero total de pacotes
        h4 = head[4] # Numero do pacote enviado
        h5 = head[5] # Se tipo for handshake: id do arquivo (crie um para cada arquivo). Se tipo for dados: tamanho do payload.
        h6 = head[6] # Pacote solicitado para recomeço quando a erro no envio.
        h7 = head[7] # Último pacote recebido com sucesso.
        h8 = head[8] # CRC Próximo projeto
        h9 = head[9] # CRC Próximo projeto
        return h0, h1, h2, h3, h4, h5, h6, h7, h8, h9


    # Escreve os logs
    def createLog(self, data, tipo):
        tempo = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        tipoMsg = data[0]
        tamMsg = len(data)
        numPacoteEnviado = data[4]
        totalPacotes = data[3]
        self.logs += f"{tempo} / {tipo} / {tipoMsg} / {tamMsg} / {numPacoteEnviado} / {totalPacotes}\n"
        
    def writeLog(self):
        with open(f'Projeto4/Logs/logServer.txt', 'w') as file:
            file.write(self.logs)

def main():
    try:
        
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
