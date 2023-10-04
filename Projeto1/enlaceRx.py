#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Camada de Enlace
####################################################

# Importa pacote de tempo
import time

# Threads
import threading

# Class
class RX(object):
  
    def __init__(self, fisica):
        self.fisica      = fisica
        self.buffer      = bytes(bytearray()) # Onde se vai armazenar os dados
        self.threadStop  = False # # True: Thread deve ser parada / False: Thread deve estar em execução
        self.threadMutex = True # True: Thread continua em execução / False: Em espera, recepção pausada / Utilizada no código para controlar o fluxo da thread de recepção
        self.READLEN     = 1024 # Tamanho máximo de leitura de cada recepção

    # Função para escrever dados no buffer
    def thread(self): 
        while not self.threadStop:
            if(self.threadMutex == True):
                rxTemp, nRx = self.fisica.read(self.READLEN) # Armazena os dados recebidos e o tamanho da mensagem
                if (nRx > 0):
                    self.buffer += rxTemp  
                time.sleep(0.01)

    # Inicia a thread de recepção
    def threadStart(self):       
        self.thread = threading.Thread(target=self.thread, args=()) # Cria a thread
        self.thread.start() # Inicia a thread

    # Faz com que a thread saia do loop e pare a execução
    def threadKill(self):
        self.threadStop = True

    # Impede que a thread de recepção receba mais dados, mas a thread ainda está em execução.
    def threadPause(self):
        self.threadMutex = False

    # Permite que a thread de recepção continue recebendo dados a partir do ponto em que foi pausada.
    def threadResume(self):
        self.threadMutex = True

    # Verifica se o buffer está vazio
    def getIsEmpty(self):
        if(self.getBufferLen() == 0):
            return(True)
        else:
            return(False)

    # Retorna o comprimento do buffer
    def getBufferLen(self):
        return(len(self.buffer))

    # Copia o conteúdo completo do buffer para uma variável b, limpa o buffer e, em seguida, retoma a recepção
    # Retorna todos os dados do buffer e esvazia o buffer completamente.
    def getAllBuffer(self, len):
        self.threadPause()
        b = self.buffer[:]
        self.clearBuffer()
        self.threadResume()
        return(b)

    # Este método pausa a recepção, copia os primeiros nData bytes do buffer para uma variável b, remove esses bytes do buffer e, em seguida, 
    # retoma a recepção
    # Retorna apenas os primeiros nData bytes do buffer e remove esses bytes do buffer, deixando os dados restantes no buffer.
    def getBuffer(self, nData):
        self.threadPause()
        b           = self.buffer[0:nData]
        self.buffer = self.buffer[nData:]
        self.threadResume()
        return(b)

    # Este método verifica se o buffer contém pelo menos size bytes de dados. Se o buffer tiver menos do que isso, 
    # ele aguarda por um curto período de tempo e verifica novamente até que haja dados suficientes.
    def getNData(self, size):
        while(self.getBufferLen() < size):
            time.sleep(0.05)                 
        return(self.getBuffer(size))

    # Limpa o buffer
    def clearBuffer(self):
        self.buffer = b""


