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
#serialName = "COM3"                  # Windows(variacao de)

class Server:
    def __init__(self, serialName):
        self.serialName = serialName
        self.logs = ''
        self.cancel_reason = None
        self.counter_repeater = 0

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
        time.sleep(.1)
        self.createLog(pack, 'receb') # Cria o log
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
    
    def checkMsgIntegrity(self, pacote, numPacote):
        self.createLog(pacote, 'receb')
        h0, h1, h2, h3, h4, h5, h6, h7, h8, h9 = self.splitHead(pacote)
        # Checando se o número do pacote enviado está correto
        if h4 != numPacote:
            print(f"\033[33mO número do pacote está errado! Por favor reenvie o pacote {numPacote}\033[0m")
            self.counter_repeater += 1
            h0 = 6 # 6 indica erro
            h7 = numPacote
            confirmacao = [h0, h1, h2, h3, h4, h5, h6, h7, h8, h9]
            responseCorrectMsg = b'' # Cria a mensagem de confirmação em bytes para enviar ao client
            for i in confirmacao: # Transforma cada elemento da lista em bytes
                i = (i).to_bytes(1, byteorder="big")
                responseCorrectMsg += i
            self.serverCom.sendData(responseCorrectMsg + b'\x00' + b'\xAA\xBB\xCC\xDD')
            #self.createLog(responseCorrectMsg + b'\x00' + b'\xAA \xBB \xCC \xDD', 'envio')
            time.sleep(0.5)

            if self.counter_repeater == 3:
                self.cancel_reason = 'Timeout'
                self.createLog(pacote, 'receb')
                self.writeLog()
                print("\033[31mTimeout, encerrando comunicação.\033[0m")
                time.sleep(0.1)
                self.closeServer()
            return h4, h3

        # Checando se o EOP está no local correto
        eop = pacote[len(pacote)-4:len(pacote)+1]
        if eop != b'\xAA\xBB\xCC\xDD':
            print(f"\033[33mO eop está no local errado! Por favor reenvie o pacote {numPacote}\033[0m")
            return h4, h3
            
        # Se tudo estiver certo, deu bom
        else:
            print("\033[32mEstá tudo certo com a mensagem! Vamos enviar a confirmação.\033[0m")
            h0 = 4 # 4 indica sucesso
            h7 = numPacote
            confirmacao = [h0, h1, h2, h3, h4, h5, h6, h7, h8, h9]
            responseCorrectMsg = b''
            for i in confirmacao:
                i = (i).to_bytes(1, byteorder="big")
                responseCorrectMsg += i
            self.serverCom.sendData(responseCorrectMsg + b'\x00' + b'\xAA\xBB\xCC\xDD')
            self.createLog(responseCorrectMsg + b'\x00' + b'\xAA\xBB\xCC\xDD', 'envio')
            time.sleep(0.5)
            return h4, h3

    # Escreve os logs
    def createLog(self, data, tipo):
        tempo = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        tipoMsg = data[0]
        tamMsg = len(data)
        numPacoteEnviado = data[4]
        totalPacotes = data[3]
        self.logs += f"{tempo} / {tipo} / {tipoMsg} / {tamMsg} / {numPacoteEnviado} / {totalPacotes}\n"

        if self.cancel_reason is not None:
            self.logs += f"{tempo} / {tipo} / 5 / {tamMsg} / {numPacoteEnviado} / {totalPacotes} / {self.cancel_reason} \n"
 
    def writeLog(self):
        with open(f'Projeto4/Logs/logServer3.txt', 'w') as file:
            file.write(self.logs)

    def receiveSacrifice(self):
        #Byte de sacrifício
        print("Esperando 1 byte de sacrifício")
        rxBuffer, nRx = self.receiveData(1)
        self.serverCom.rx.clearBuffer()
        time.sleep(.1)
        
serialName = "COM3"

def main():
    try:
        server = Server('COM3')
        server.startServer()

        server.receiveSacrifice()

        # HandShake
        print("Esperando o Handshake do Client...\n")
        
        pack, lenpack = server.receiveHandshake(15)
        print("\033[32mHandshake recebido com sucesso, enviando resposta\033[0m")
        server.sendData(pack)
        time.sleep(0.5)

        # Recebendo o pacote
        data = b'' # Dados que serão armanezados nessa variável
        numPack = 1 # Número do pacote que está sendo recebido
        
        while True:
            print(f"Recebendo informações do pacote {numPack}")
            head, lenhead = server.receiveData(10)
            len_payload = head[5] # Definimos essa variável (h3) para saber o tamanho do payload
            payloadEOP, lenpayloadEOP = server.receiveData(len_payload + 4)
            numPackReceived, numPackTotal = server.checkMsgIntegrity(head + payloadEOP, numPack)
            if numPackReceived == numPack:
                data += payloadEOP[0:lenpayloadEOP - 4]
                numPack += 1 # Caso o pacote esteja correto, passamos para o próximo
            if numPackReceived == numPackTotal -1: # Se todos os pacotes foram recebidos, saímos do loop
                data += payloadEOP[0:lenpayloadEOP - 4]
                break
        
        # Escrevendo o arquivo
        print("Escrevendo o arquivo")
        path = "Projeto4/Images/imgRx.jpg"
        with open(path, 'wb') as file:
            file.write(data)
        file.close()
        print("Arquivo escrito com sucesso!")

        server.writeLog()
        server.closeServer()

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        server.closeServer()
        
    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
