import math
def calcula_duracao(boudRate, tamanhoArquivo, tamanhoHead, tamanhoEop, tamanhoPayload,tambyte):
    #BoudRate = quantidade de bytes por segundo
    #tamanho = tamanho do arquivo em bytes (incluso head e eop e)
    #tamanhoHead = tamanho do head em bytes
    #tamanhoEop = tamanho do eop em bytes
    #tamanhoPayload = tamanho do payload em bytes

    # boudRate -> bits/segundo
    # tamanhoArquivo -> quantos bytes no arquivo
    # tamanhoHead -> quantidade d bytes no HEAD
    # tamanhoEop -> quantidade d bytes no EOP
    # tamanhoPayload -> qnt d bytes no payload
    # bitPbyte -> 8, 10 ou 11

    qntPacotes = tamanhoArquivo/tamanhoPayload
    qntPacotes = math.ceil(qntPacotes)
    
    print("Quantidade de pacotes:",qntPacotes)
    
    bitHead = tamanhoHead*qntPacotes*tambyte
    bitArquivo = tamanhoArquivo*tambyte
    bitEop = tamanhoEop*qntPacotes*tambyte

    soma = bitHead + bitArquivo + bitEop #soma dos bits a serem enviados
    tempo = soma/boudRate
    return print('A duração do envio do arquivo será:', tempo)

#calcula_duaracao(115200, 2000, 10, , None, 110, 11)

import math

def calcula_eop(boudRate, tamanhoArquivo, tamanhoHead, tempo, tamanhoPayload, tambyte):
    # boudRate -> bits/segundo
    # tamanhoArquivo -> quantos bytes no arquivo
    # tamanhoHead -> quantidade d bytes no HEAD
    # tempo -> tempo de envio do arquivo em segundos
    # tamanhoPayload -> qnt d bytes no payload
    # tambyte -> 8, 10 ou 11

    qntPacotes = tamanhoArquivo/tamanhoPayload
    qntPacotes = math.ceil(qntPacotes)

    bitHead = tamanhoHead*qntPacotes*tambyte
    bitArquivo = tamanhoArquivo*tambyte

    soma = bitHead + bitArquivo #soma dos bits a serem enviados
    bitEop = (boudRate*tempo - soma)/qntPacotes/tambyte

    return print('A quantidade de bits do EOP é:', bitEop)

#calcula_eop(115200, 2000, 10, 0.22, 110, 11)

def calcula_boudRate(tamanhoArquivo, tamanhoHead, tempo, tamanhoPayload, tambyte):
    # boudRate -> bits/segundo
    # tamanhoArquivo -> quantos bytes no arquivo
    # tamanhoHead -> quantidade d bytes no HEAD
    # tempo -> tempo de envio do arquivo em segundos
    # tamanhoPayload -> qnt d bytes no payload
    # tambyte -> 8, 10 ou 11

    qntPacotes = tamanhoArquivo/tamanhoPayload
    qntPacotes = math.ceil(qntPacotes)

    bitHead = tamanhoHead*qntPacotes*tambyte
    bitArquivo = tamanhoArquivo*tambyte

    soma = bitHead + bitArquivo #soma dos bits a serem enviados
    boudRate = soma/tempo

    return print('O BoudRate é:', boudRate)

calcula_boudRate(2000, 10, 0.22, 110, 10)
