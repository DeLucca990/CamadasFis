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
class TX(object):
 
    def __init__(self, fisica):
        self.fisica      = fisica
        self.buffer      = bytes(bytearray()) # Onde se vai armazenar os dados
        self.transLen    = 0 # Comprimento da mensagem atual
        self.empty       = True # True: Buffer vazio / False: Buffer com dados
        self.threadMutex = False # True: Thread permite a execução / False: Em espera, transmissão pausada / Utilizada no código para controlar o fluxo da thread de transmissão.
        self.threadStop  = False # True: Thread deve ser parada / False: Thread deve estar em execução

    # Função para escrever dados no buffer
    def thread(self):
        while not self.threadStop: # Enquanto a thread não for parada
            if(self.threadMutex): # Se a thread estiver em execução
                self.transLen    = self.fisica.write(self.buffer) # Escreve no buffer
                self.threadMutex = False # Pausa a thread

    # Inicia a thread de transmissão
    def threadStart(self):
        self.thread = threading.Thread(target=self.thread, args=()) # Cria a thread
        self.thread.start() # Inicia a thread

    # Faz com que a thread saia do loop e pare a execução
    def threadKill(self):
        self.threadStop = True

    # Impede que a thread de transmissão transmita mais dados, mas a thread ainda está em execução.
    def threadPause(self):
        self.threadMutex = False

    # Permite que a thread de transmissão continue transmitindo dados a partir do ponto em que foi pausada.
    def threadResume(self):
        self.threadMutex = True

    # Função para escrever dados no buffer
    def sendBuffer(self, data):
        self.transLen   = 0
        self.buffer = data
        self.threadMutex  = True 

    # Retorna o comprimento do buffer
    def getBufferLen(self):
        return(len(self.buffer))

    # Retorna o comprimento da última transmissão realizada
    def getStatus(self):
        return(self.transLen)
        
    # Retorna o estado da thread de transmissão (True: Em execução / False: Em espera)
    def getIsBussy(self):
        return(self.threadMutex)

