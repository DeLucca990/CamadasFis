#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time
import numpy as np
import os
import math
from datetime import datetime
from crccheck.crc import Crc16

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
com1 = enlace('COM3')

class Client:
    def __init__(self, file, serialName):
        self.serialName = serialName
        self.cancel_reason = None
        self.head = None
        self.file = file
        self.eop = b'\xAA\xBB\xCC\xDD'
        self.payloads = 0
        self.h0 = 0 # Tipo da Mensagem
        self.h1 = b'\x00' # Se tipo for 1: número do servidor. Qualquer outro tipo: livre 
        self.h2 = b'\x00' # Livre
        self.h3 = 0 # Numero total de pacotes
        self.h4 = 0 # Numero do pacote enviado
        self.h5 = 0 # Se tipo for handshake: id do arquivo (crie um para cada arquivo). Se tipo for dados: tamanho do payload.
        self.h6 = b'\x00' # Pacote solicitado para recomeço quando a erro no envio.
        self.h7 = 0 # Último pacote recebido com sucesso.
        self.h8 = b'\x00' # CRC 
        self.h9 = b'\x00' # CRC 
        self.logs = ''

    def startClient(self):
        self.clientCom = enlace(self.serialName)
        self.clientCom.enable()

    def closeClient(self):
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        self.clientCom.disable()
        exit()
    
    def sendSacrifice(self):
        self.clientCom.sendData(b'\x00')
        time.sleep(0.1)
        print("Enviando byte de sacrifício")
        
    # Cria os payloads
    def createPayloads(self):
        size = 114
        self.payloads = []
        for i in range(0, len(self.file), size):
            self.payloads.append(self.file[i:i + size]) # Divide os pacotes em tamanhos iguais a 114 bytes
        return self.payloads

    def createCRC(self):
        data = self.payloads[int.from_bytes(self.h4,"big")-1]
        # if int.from_bytes(self.h4,"big") - 1 == 2:
        #     data = self.payloads[1]
        # else:
        crc1, crc2 = Crc16.calc(data).to_bytes(2, byteorder="big")
        self.h8 = crc1.to_bytes(1, byteorder="big")
        self.h9 = crc2.to_bytes(1, byteorder="big")

    # Define o tipo da mensagem
    def TypeMsg(self, n):
        self.h0 = (n).to_bytes(1, byteorder="big")
        # Mensagem do tipo Handshake
        if n == 1:
            self.h5 = b'\x00'
        # Mensagem do tipo dados
        elif n == 3:
            self.h5 = len(self.payloads[int.from_bytes(self.h4,"big")-1]) # -1 pois o index começa em 0
            self.h5 = (self.h5).to_bytes(1, byteorder="big")

    # Define a mensagem
    def numMsg(self, n):
        self.h4 = (n).to_bytes(1, byteorder="big")  # numero pacote
        self.h7 = (n-1).to_bytes(1, byteorder="big")    # numero ultimo pacote
    
    # Define o número total de pacotes
    def numPack(self):
        lenPayload = len(self.file)
        h3 = math.ceil(lenPayload/114)
        self.h3 = (h3).to_bytes(1, byteorder="big")

    # Constrói o head
    def buildHead(self):
        self.head = self.h0 + self.h1 + self.h2 + self.h3 + self.h4 + self.h5 + self.h6 + self.h7 + self.h8 + self.h9
    
    # Constrói o pacote
    def buildDatagram(self):
        return self.head + self.payloads[int.from_bytes(self.h4,"big")-1] + self.eop
    
    # Checa o tempo máximo para a resposta do servidor
    def SendWait(self, pacote):
        timeMax = time.time()
        while True: 
            self.clientCom.sendData(pacote)
            time.sleep(.1)
            self.createLog(pacote, 'envio')
            time.sleep(.5)
            len_conf = self.clientCom.rx.getBufferLen()
            time.sleep(.5)
            if len_conf != 0:
                confirmacao, lenConfimacao = self.clientCom.getData(15)
                if type(confirmacao) == str:
                    print(confirmacao)
                else:
                    return confirmacao
            else:
                timeF = time.time()
                if timeF - timeMax > 20:
                    self.cancel_reason = "Timeout"
                    print("\033[31mServidor não respondeu. Cancelando comunicação.\033[0m")
                    self.createLog(pacote, 'envio')
                    break

    # Handshake
    def handshake(self):
        payload = b'\x00'
        self.TypeMsg(1)
        self.h3 = b'\x00'
        self.h4 = b'\x00'
        self.h7 = b'\x00'
        self.buildHead()
        datagram = self.head + payload + self.eop
        return self.SendWait(datagram)
    
    # Checa o tipo de mensagem na confirmação enviada pelo servidor
    def checkTypeMsg(self, confirmacao):
        if confirmacao[0] == 4: # 4 indica sucesso (confirmacao[0] = h0)
            self.createLog(confirmacao, 'receb')
            print(f"Número do pacote: {confirmacao[7]}")
            print("\033[32mTudo certo! O servidor recebeu o pacote corretamente.\033[0m")
        else:
            self.createLog(confirmacao, 'receb')
            numPacoteCorreto = confirmacao[7]
            print(f"\033[33mAlgo deu errado no envio. Precisamos reenviar o pacote {numPacoteCorreto}\033[0m")
            return numPacoteCorreto
    
    # Escreve os logs
    def createLog(self, data, tipo):
        tempo = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        tipoMsg = data[0]
        tamDatagram = len(data)
        numPacoteEnviado = data[4]
        totalPacotes = data[3]
        self.logs += f"{tempo} / {tipo} / {tipoMsg} / {tamDatagram} / {numPacoteEnviado} / {totalPacotes}\n"

        if self.cancel_reason is not None:
            self.logs += f"{tempo} / {tipo} / 5 / {tamDatagram} / {numPacoteEnviado} / {totalPacotes} / {self.cancel_reason}\n"
        
    def writeLog(self):
        with open(f'Projeto5/Logs/logClient2.txt', 'w') as file:
            file.write(self.logs)

serialName = "COM3"
path = 'Projeto5/Images/imgTx.jpg'
file = open(path, "rb").read()

def main():
    try:
        client = Client(file, "COM3")
        client.startClient()

        # Envia byte de sacrifício
        client.sendSacrifice()

        # Handshake
        print("Enviando Handshake\n")
        if client.handshake() is None:
            client.closeClient()
        else:
            print("\033[32mHandshake enviado com sucesso!\033[0m")
        
        # Envia os pacotes
        print("Iniciando envio de pacotes")
        client.createPayloads()
        client.numPack()
        # h3 = número total de pacotes
        # h4 = número do pacote sendo enviado
        h4 = 1

        c = 0
        while h4 < int.from_bytes(client.h3, "big"):
            print(f"Enviando informações referentes ao pacote {h4}")
            time.sleep(0.1)
            client.numMsg(h4) # Define o número do pacote
            client.createCRC() # Cria o protocolo CRC
            print(f"\033[35mCRC: {client.h8} {client.h9}\033[0m")
            client.TypeMsg(3) # 3 = dados
            client.buildHead()
            pacote = client.buildDatagram()
            confirmacao = client.SendWait(pacote) # Envia o pacote e espera a confirmação do servidor

            if confirmacao is None: # Se não houver resposta do servidor, encerra a comunicação
                client.writeLog()
                client.closeClient()
            else:
                numPacoteCorreto = client.checkTypeMsg(confirmacao)
                if numPacoteCorreto is None: # Se o número do pacote estiver errado
                    if h4 == 7: # Se o número do pacote for 7, pula para o 9 (FORÇA O ERRO)
                        h4 += 1
                    else:
                        h4 += 1
                    c += 1
                else: # Se o número do pacote estiver correto, envia o próximo
                    h4 = numPacoteCorreto
                    c = numPacoteCorreto - 1 

        client.writeLog()
        client.closeClient()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
