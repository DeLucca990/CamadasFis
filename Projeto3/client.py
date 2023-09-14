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


def verifica_time(tempo_inicial):
    tempo_atual = time.time()
    while(RX.getBufferLen() < TX.size): #ver aqui direito a variavel
        tempo_passado = tempo_atual - tempo_inicial

        if tempo_passado > 5:
            return True
        else:
            return False
    
def main():
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()

        com1.fisica.flush()

        # Iniciando o cronometro
        cronometro_client = time.time()

        print("Abriu a comunicação")

        def verifica_time():
            inicial_time = time.time()
            while(self.getBufferLen() < size):
                clock = time.time() - inicial_time
                time.sleep(0.05)
                if clock >= 5:
                    print("Servidor inativo")
                    return (b'\xFF')     

        EOP = b'\x00\x00\x01'
        handshake_message = b'HEAD\x01\x01\x00\x00\x00\x00\x00\x00' + b'\x01' + EOP
        print(f"Enviando o seguinte HandShake {handshake_message} de tamanho {len(handshake_message)}")
        
        # 0-tipo [0:Handshake,1:Resposta Handshake,2:Envio de comandos,3:Acknowledge],
        # 1-origem [0:Client, 1:Server],
        # 2-destino [0:Server, 1:Client],
        # 3-tamanho total do arquivo [quantidade de bytes que serão fracionados em n pacotes],
        # 4-tamanho total do arquivo [quantidade de bytes que serão fracionados em n pacotes],
        # 5-pacotes a serem enviados [número n],
        # 6-numero do pacote atual [entre 0 e n-1, dado n pacotes],
        # 7-quantidade de bytes no payload atual [entre 0 e 114],
        # 8-integridade do pacote [1:OK,0:solicita reenvio]
        # 9-porcentagem de bytes que faltam para a imagem (complementar do tamanho total)

        # HANDSHAKE
        TryAgain = True
        while TryAgain:
            print("-------------------------")
            print("         HANDSHAKE        ")
            print("-------------------------\n")
            print("Handshake pelo client sendo enviado em alguns segundos... \n")

            com1.sendData(np.asarray(handshake_message))
            time.sleep(0.1)

            print("Handshake enviado, esperando resposta do server... \n")
            print(f'Númeo de bytes enviados: {com1.tx.transLen}')

            rxBufferHandshake, rxnHandshake = com1.getData(16)
            time.sleep(1)

            #print(f'Recebeu o handshake do server de tamanho {rxnHandshake}')

            if rxBufferHandshake[12:13] == b'\x02':
                if not verifica_time():
                    print("Handshake feito com sucesso!")
                    print(f"O server recebeu o byte: {rxBufferHandshake}")
                    print("Vamos iniciar a transmissao do pacote\n")
                    TryAgain = False
                else:
                    resposta = input("Tentar novamente (S/N)?")
                    if resposta.lower() == "s":
                        rxBufferHandshake[12:12] == b'\x01'
                        TryAgain = True
                    else: 
                        TryAgain = False
                        print("Ocorreu um erro. Tente novamente depois")
            
                    
            # Quando o server não responde essa resposta é autogerada
            # elif rxBufferHandshake == b'\xFF':
            #     resposta = input("Tentar novamente (S/N)?")
            #     if resposta.lower() == "s":
            #         TryAgain = True
            #     else: 
            #         TryAgain = False
            #         print("Ocorreu um erro. Tente novamente depois")
        
        # Definindo o PAYLOAD
        filepath = "Projeto3\payload.txt"
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
            Head = b'HEAD' + currentPacks + b'/' + lenPacks_bin + b'\x00\x00\x01'
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
                    rxNextPack, rxnNextPack = com1.getData(16)
                    if rxNextPack[12:13] == b'\x0F':
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
