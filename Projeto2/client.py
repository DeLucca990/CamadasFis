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
        bytes_list = [b"\x00\x00\x00\x00",b"\x00\x00\xbb\x00", b"\xbb\x00\x00", b"\x00\xbb\x00", b"\x00\x00\xbb", b"\x00\xaa", b"\xbb\x00", 
              b"\x00", b"\xbb"]
        num_comands = np.random.randint(10, 30)
        cmd_list = []
        while len(cmd_list) < num_comands:
            list_index = np.random.randint(0,8)
            cmd_list.append(bytes_list[list_index])

        print("Iniciou o main")

        com1 = enlace(serialName)
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()

        # Byte de sacrifício
        time.sleep(.2)
        com1.sendData(b'\x00')
        time.sleep(1)

        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
        print("Enviando comandos")

        # Teste de transamissão
        nPacotes = num_comands.to_bytes(1, byteorder='big')
        com1.sendData(np.asarray(nPacotes)) #as array apenas como boa pratica para casos de ter uma outra forma de dados
        print(f"Numero de comandos: {num_comands}")
        time.sleep(1)
        #faça um print para avisar que a transmissão vai começar.
        print("vai começar a transmissão")
        x=0
        for i in cmd_list:
            # Tamanho do pacote a ser enviado
            txBufferLen = len(i)

            # Pacote a ser enviado 
            txBuffer = i        

            # Transformando o tamanho do pacote a ser enviado em bytes
            txBufferHeader = txBufferLen.to_bytes(1, byteorder="big")

            # Enviando o tamanho do pacote em bytes
            com1.sendData(txBufferHeader)
            time.sleep(0.1)

            # Enviando o pacote
            com1.sendData(txBuffer)
            time.sleep(0.1)
            x+=1

            print(f"Enviando comando {txBuffer}")
            print(f"Tamanho do pacote: {txBufferLen}")
            print(f"Estamos no comando: {x} de {num_comands}")
            print("-"*50)
            time.sleep(1)
        
        print("Comandos enviados com sucesso")
        print("Esperando resposta do server")

        start_time = time.time() # Tempo inicial
        
        n_cmd_rx,_ = com1.getData(1)
        n_cmd_rx_int = int.from_bytes(n_cmd_rx, byteorder='big')

        # Verifica se houve timeout
        if time.time() - start_time >= 5:
            print("\033[31mTime-out: Big F\033[0m")
        else:
            while time.time() - start_time < 5:
                len_ = com1.rx.getBufferLen()
                if len_ == 0 and n_cmd_rx_int == num_comands:
                    print("\033[32mResposta recebida pelo server. Boraaa\033[0m")
                    break
                else:
                    print("\033[33mResposta não recebida pelo server. Ele é muito troll\033[0m")
                    break
        
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
