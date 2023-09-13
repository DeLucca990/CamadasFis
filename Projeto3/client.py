#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 

from math import ceil
from enlaceClient import *
from enlaceRxClient import *
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

def main():
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()

        # Iniciando o cronometro
        cronometro_client = time.time()

        print("Abriu a comunicação")

        EOP = b'\x00\x00\x01'
        handshake_message = b'HEAD\x01/\x01\x00\x00\x00' + b'\x01' + EOP
        print(f"Enviando o seguinte HandShake {handshake_message} de tamanho {len(handshake_message)}")
        
        
        # HANDSHAKE
        TryAgain = True
        while TryAgain:
            print("-------------------------")
            print("         HANDSHAKE        ")
            print("-------------------------\n")
            print("Handshake pelo client sendo enviado em alguns segundos... \n")

            com1.sendData(handshake_message)
            time.sleep(0.1)

            print("Handshake enviado, esperando resposta do server... \n")
            print(f'Númeo de bytes enviados: {com1.tx.transLen}')

            rxBufferHandshake, rxnHandshake = com1.getData(14)

            #print(f'Recebeu o handshake do server de tamanho {rxnHandshake}')

            if rxBufferHandshake[10:11] == b'\x02':
                print("Handshake feito com sucesso!")
                print(f"O server recebeu o byte: {rxBufferHandshake}")
                print("Vamos iniciar a transmissao do pacote\n")
                TryAgain = False
            # Quando o server não responde essa resposta é autogerada
            elif rxBufferHandshake == b'\xFF':
                resposta = input("Tentar novamente (S/N)?")
                if resposta.lower() == "s":
                    TryAgain = True
                else: 
                    TryAgain = False
                    print("Ocorreu um erro. Tente novamente depois")
        
        # Definindo o PAYLOAD
        filepath = "./payload.txt"
        payloadSize = 50

        packageList = []
        with open(filepath, "rb") as file:
            binRead = file.read()
            binArray = bytearray(binRead)
            lenPacks = (len(binArray)/payloadSize)
            for i in range(0, int(ceil(lenPacks))):
                packageList.append(binArray[:payloadSize])
                del(binArray[:payloadSize])

        datagramas = []
        for i in range(len(packageList)):
            lenPacks_bin = len(packageList).to_bytes(1, byteorder="big") # Converte o tamanho do pacote para bytes
            currentPacks = (i+1).to_bytes(1, byteorder="big") # Converte o número do pacote para bytes
            Head = b'HEAD' + currentPacks + b'/' + lenPacks_bin + b'\x00\x00\x00'
            string_bytes_pack = Head + packageList[i] + EOP # Concatena todos os bytes do pacote
            datagramas.append(string_bytes_pack)

        # Envio do datagrama

        print("------------------------------------------")
        print("         INICIANDO ENVIO DE PACOTES      ")
        print("------------------------------------------\n")
        print("Pacote será enviado em alguns segundos... \n")

        n = 0
        while n < (len(datagramas)):
            print(n)

            pacoteEnviar = datagramas[n]

            numeroBytesPack = (len(datagramas[n])).to_bytes(2, byteorder="big")
            com1.sendData(np.asarray(numeroBytesPack))

            print("------------------------------------------\n")
            print("Enviei o número de bytes a serem transmitidos\n")

            rxBufferPackSize, rxnPackSize = com1.getData(2)


            if rxBufferPackSize == numeroBytesPack:
                lenBytesPack = len(datagramas[n])
                print(f"Vamos transmitir: {lenBytesPack} bytes")

                print(f"Quero mandar esse pacote: {pacoteEnviar}\n")

                com1.sendData(np.asarray(pacoteEnviar))

                if n != len(datagramas):
                    rxNextPack, rxnNextPack = com1.getData(14)
                    if rxNextPack[10:11] == b'\x0F':
                        print("O server deu o sinal verde, posso enviar o próximo pacote\n")
                        n += 1
                    else:
                        print("Ocorreu um erro com os pacotes")
                        print(f"Recebeu o pacote que é para reenviar {rxNextPack}")
                else:
                    print("Transmissão encerrada!")
                
                
        tempo_final = time.time()
        tempo_total = tempo_final - cronometro_client
        #velocidade = len(txBuffer)/tempo_total

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
