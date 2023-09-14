#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
from datagrama import *
from stringToDatagram import *
import time
import numpy as np
import os

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)

previousPackageIndex = -1 # Index do pacote anterior

if os.path.exists("recebido.txt"):
    os.remove("recebido.txt")

com1 = enlace(serialName)
com1.enable()
payload = ''

def handshake():
    handshake_head = Head('HH', 'SS', 'CC') # 'HH' (handshake) com remetente 'SS' (servidor) e destinatário 'CC' (cliente)
    handshake_head.buildHead()
    handshake = Datagrama(handshake_head, '') # Cria o Datagrama com o Head e sem Payload
    com1.sendData(bytes(handshake.head.finalString + handshake.EOP, "utf-8"))
    print('Handshake recebido, enviando confirmação')

def acknowledge(): # Envia confirmação de recebimento
    confirmationHead = Head('88', 'SS', 'CC') # '88' (confirmação) com remetente 'SS' (servidor) e destinatário 'CC' (cliente)
    confirmationHead.buildHead()
    confirmation = Datagrama(confirmationHead, '') # Cria o Datagrama com o Head e sem Payload
    confirmationString = confirmation.head.finalString + confirmation.EOP # Constrói uma string de confirmação concatenando o cabeçalho e o EOP
    while len(confirmationString) < 22: #27
        confirmationHead = Head('88', 'SS', 'CC')
        confirmationHead.buildHead()
        confirmation = Datagrama(confirmationHead, '')
        confirmationString = confirmation.head.finalString + confirmation.EOP
    print(confirmationString)
    com1.sendData(bytes(confirmationString, "utf-8"))

def not_acknowledge(): # Envia pedido de reenvio
    confirmationHead = Head('99', 'SS', 'CC')
    confirmationHead.buildHead()
    confirmation = Datagrama(confirmationHead, '')
    confirmationString = confirmation.head.finalString + confirmation.EOP
    while len(confirmationString) < 22: #27
        confirmationHead = Head('99', 'SS', 'CC')
        confirmationHead.buildHead()
        confirmation = Datagrama(confirmationHead, '')
        confirmationString = confirmation.head.finalString + confirmation.EOP
    #print(confirmationString)
    com1.sendData(bytes(confirmationString, "utf-8"))


def main():
    # Declaram-se as variáveis globais para que elas possam ser modificadas dentro da função.
    global payload
    global previousPackageIndex
    try:
        #Byte de sacrifício
        print("Esperando 1 byte de sacrifício")
        rxBuffer, nRx = com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(.1)

        print("Comunicação aberta com sucesso")

        # Handshake
        print("Esperando handshake...")
        rxLen = com1.rx.getBufferLen() # Obtém o comprimento do buffer de recepção.
        while rxLen == 0: # Inicia um loop que aguarda até que haja algo no buffer de recepção.
            rxLen = com1.rx.getBufferLen()
            time.sleep(.5)
        rxBuffer, nRx = com1.getData(rxLen) # Quando há dados no buffer de recepção, obtém esses dados

        decoded = rxBuffer.decode() # Decodifica os dados recebidos em UTF-8.
        datagram = stringToDatagram(decoded) # Converte a string recebida em um objeto Datagrama. 

        if decoded.startswith('HH'): # Verifica se o pacote recebido é um handshake
            handshake()
        else:
            raise Exception("Erro: pacote recebido não é handshake") # Se não for handshake levanta um erro
        
        com1.rx.clearBuffer() # Limpa buffer após o processo de handshake

        # Recebendo pacotes

        print("Iniciando recebimento de pacotes")
        print("-----------------------------------------")

        while True:
            rxLen = com1.rx.getBufferLen()
            while rxLen == 0:
                rxLen = com1.rx.getBufferLen()
                time.sleep(1)
            rxBuffer, nRx = com1.getData(rxLen)
            time.sleep(0.3)

            decoded = rxBuffer.decode() # Decodifica os dados recebidos em UTF-8.
            datagram = stringToDatagram(decoded) # Converte a string recebida em um objeto Datagrama.

            print(int(datagram.head.payloadSize))
            print(len(datagram.payload))

            if decoded.startswith('DD'): # Verifica se o pacote recebido é um pacote de dados
                if decoded.endswith('ABC'): # Verifica se o pacote recebido tem o EOP no local correto
                    if int(datagram.head.payloadSize) == len(datagram.payload): # Compara o tamanho do payload no cabeçalho com o tamanho real do payload. Isso é usado para verificar a integridade do pacote.
                        if int(datagram.head.currentPayloadIndex) == previousPackageIndex + 1: # Verifica se o índice do pacote recebido é o esperado (ou seja, se é o próximo pacote na sequência).
                            print(f"Pacote {previousPackageIndex+1} recebido com sucesso")
                            payload += datagram.payload
                            acknowledge()
                            previousPackageIndex += 1
                            print(previousPackageIndex)
                            # Se todas as condições acima forem atendidas, o pacote é considerado recebido com sucesso. Os dados do pacote são adicionados ao payload, uma confirmação é enviada ao servidor, e o índice do pacote anterior é atualizado.
                        else:
                            print("Index do pacote errado, pedindo reenvio do pacote")
                            not_acknowledge() # Solicita o reenvio do pacote
                        
                        print(f"Indice do payload atual:{int(datagram.head.currentPayloadIndex) + 1}")
                        print(f"Indice total do payload: {int(datagram.head.totalPayloads)}")
                        if int(datagram.head.currentPayloadIndex) + 1 == int(datagram.head.totalPayloads): # Verifica se todos os pacotes foram recebidos com sucesso com base nos índices de payload. Se todos os pacotes foram recebidos, o loop é interrompido.
                            print("Todos pacotes recebidos com sucesso")
                            break
                    else:
                        print("Tamanho do payload errado, pedindo reenvio do pacote")
                        not_acknowledge()
                else:
                    print("EoP no local errado, pedindo reenvio do pacote")
                    not_acknowledge()
                        
                print("--------------------------------------------------")    
                com1.rx.clearBuffer()	
            else:
                print("Tipo do pacote errado, pedindo reenvio do pacote")
                not_acknowledge()

        # Salvando arquivo
        decodedPayload = payload
        print("Salvando arquivo")
        with open("recebido.txt", "w") as arquivo:
            arquivo.write(decodedPayload)

        acknowledge()

        # Encerra comunicação
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
