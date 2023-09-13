#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
from enlaceRx import * 
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

        com1.fisica.flush()

        # Iniciando Cronômetro
        cronometro_server = time.time()

        print("Abriu a comunicação")

        # HANDSHAKE
        TryAgain = True
        while TryAgain:
            print("-------------------------")
            print("         HANDSHAKE        ")
            print("-------------------------\n")
            print("Vamos estabelecer o Handshake com o Client")

            # os mesmos 2 bytes que foram enviados vão ser recebidos aqui: que são exatamente o tamanho total de byte

            txBufferHandshake, tRxHandshake = com1.getData(14)
            EOP = b'\x00\x00\x01'
            respostaServer = b'HEAD\x01/\x01\x00\x00\x00' + b'\x02' + EOP

            # de bytes transformando para decimal de novo, que é como iremos usar no resto da comunicação

            print("Agora servidor está enviando o Handshake de volta para o client")

            if txBufferHandshake[10:11] == b'\x01':
                time.sleep(1)
                com1.sendData(respostaServer)
                print("Respondi o Handshake e posso começar a transmissão")
                TryAgain = False
        
        print("Pronto para receber os pacotes\n")

        # RECEBER DATAGRAMAS

        EnvioNaoCompleto = True

        nOldPackage = 0
        dataReceived = []

        print("------------------------------------------------")
        print("         INICIANDO RECEBIMENTO DE PACOTES      ")
        print("------------------------------------------------\n")

        forcarErro = False
        forcarErroNbytes = True

        while EnvioNaoCompleto:
            print("Vamos estabelecer o recebimento dos datagramas com o Client!")
            # os mesmos 2 bytes que foram enviados vão ser recebidos aqui: que são exatamente o tamanho total de byte
            txPackSize, tRxNPackSize= com1.getData(2)

            rxBufferResposta = int.from_bytes(txPackSize, byteorder ="big")

            print("Agora o servidor está enviando o número de bytes do pacote a ser recebido")

            com1.sendData(np.asarray(txPackSize))

            print("Manda de novo o número de bytes que vai receber\n")

            txPack, txnPack = com1.getData(rxBufferResposta)

            print("-----------------------------------")
            print("        ANALISANDO PACOTES...    ")
            print("-----------------------------------\n")
            print(f"Pacote recebido:{txnPack}\n")

            if forcarErroNbytes:
                BytesErrados = txPack[0:10] + b'\x00\x01\x02\x00\x00\x00\x02' + txPack[11:rxBufferResposta]
                txPack = BytesErrados
                print(f"BYTES ERRADOS:{BytesErrados}")
            
            EOP = txPack[(rxBufferResposta-3):rxBufferResposta]
            print(f"Esse é o EOP:{EOP}\n")
            CurrentPack = txPack[4:5]

            print("-------------------------\n")
            print(f"Pacote atual:{CurrentPack}")
            nCurrentPack = int.from_bytes(CurrentPack, byteorder="big")
            print(f"Pacote atual em int:{nCurrentPack}\n")
            TotalPacks = txPack[6:7]
            nTotalPacks = int.from_bytes(TotalPacks, byteorder="big")
            print("-------------------------\n")

            print(f'Número total de pacotes: {nTotalPacks}')

            sinal_verde = b'HEAD\x01/\x01\x00\x00\x00' + b'\x0F'+ EOP

            if forcarErro:
                nCurrentPack -= 1

            if nCurrentPack == (nOldPackage + 1) and EOP == b'\x00\x00\x01':
                print(f"Pacote recebido está certo! Vou enviar o sinal verde: {sinal_verde}")
                dataReceived.append(txPack)
                com1.sendData(sinal_verde)
                nOldPackage+= 1
                if nCurrentPack == nTotalPacks and EOP == b'\x00\x00\x01':
                    print("Recebi todos os pacotes!")
                    EnvioNaoCompleto = False
            else:
                if forcarErro:
                    print("Recebi o pacote errado!")
                    print("O Client vai ter que me enviar o mesmo pacote")
                    forcarErro = False
                    CurrentPackDatagrama = b'HEAD\x01/\x01\x00\x00\x00' + CurrentPack + EOP
                    print(CurrentPackDatagrama)
                    com1.sendData(CurrentPackDatagrama)
                elif forcarErroNbytes:
                    print("Recebi o número de bytes errado! O EOP está fora de ordem")
                    print("O client vai ter que me reenviar o pacote")
                    forcarErroNbytes = False
                    CurrentPackDatagrama = b'HEAD\x01/\x01\x00\x00\x00' + CurrentPack + b'\x00\x00\x01'
                    print(CurrentPackDatagrama)
                    com1.sendData(CurrentPackDatagrama)
            # o server deve enviar uma mensagem para o client solicitando o reenvio do pacote, seja por
            # não ter o payload esperado, ou por não ser o pacote correto
        print(f"Todos os dados aqui: {dataReceived}")

        organizedData = b''

        for j in range(len(dataReceived)):
            currentByteStr = dataReceived[j]
            lenCurrentByteStr = len(currentByteStr)
            payload = currentByteStr[10:(lenCurrentByteStr-3)]
            organizedData += payload

        print(organizedData)

        # with open('receivedFile.txt','wb') as f:
        #     f.write(organizedData)

        tempo_final = time.time()
        tempo_total = tempo_final - cronometro_server


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
