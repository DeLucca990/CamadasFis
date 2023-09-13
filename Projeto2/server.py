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
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)

        # Esperando Byte de sacrifício
        com1.enable()
        print("esperando 1 byte de sacrifício")
        rxBuffer, nRx = com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(.1)
        print("Abriu a comunicação")
        print("Vai começar a recepção")
        
        # Recbendo a quantidade de comandos que será enviada posteriormente
        num_cmd,t = com1.getData(1)
        num_cmd_int = int.from_bytes(num_cmd, byteorder='big')
        print(f'Número de comandos recebidos: {num_cmd_int}')
            
        x = 0
        while x < num_cmd_int:
            # Recebndo o tamanho do pacote
            rxBufferHeader, _= com1.getData(1)
            rxBufferHeader_int = int.from_bytes(rxBufferHeader, byteorder='big')

            rxBufferPack, _= com1.getData(rxBufferHeader_int)
            rxBufferPack_int = int.from_bytes(rxBufferPack, byteorder='big')
            
            print(f"-"*50)
            time.sleep(1.2)
            x += 1
        print("Pacotes recebidos com sucesso")
        
        # Enviando os pacotes recebidos de volta ao client
        print("Enviando os pacotes recebidos de volta ao client")
        com1.sendData(num_cmd)

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
