#include <Arduino.h>

int pinClient = 5; 
char message[] = "Camadas Fisicas";
float baudrate = 9600;

void setup() {
  pinMode(pinClient, OUTPUT);
  Serial.begin(baudrate); 
  digitalWrite(pinClient, HIGH);
}

float timeSkipper(float skipTime=1, float baudrate=9600, float T0=0) { // Função para criar os atrasos necessários
  double clock = 1 / (21 * pow(10, 6)); // Período do clock
  double T = 1 / baudrate; //Período de 1 bit (quanto tempo levará para ser transmitido)
  int numberOfClocks = ceil(T / clock) + 1; // Número de ciclos do clock
  for (int i = 0; i < int(numberOfClocks * skipTime); i++) {
    asm("NOP"); // Cria o atraso necessário
  }
}

void loop() {
  for (int i = 0; i < strlen(message); i++) {
    char currentChar = message[i];

    digitalWrite(pinClient, 0); // Pino LOW (indica início de transmissão)
    timeSkipper(); // Essa função sempre será chamada para criar o atraso

    for (int j = 0; j < 8; j++) {
      int currentBit = 1 & (currentChar >> j); 
      digitalWrite(pinClient, currentBit);
      timeSkipper();
    }

    int amountOf1s = 0; // Conta a quantidade de bits 1 no caractere
    for (int j = 0; j < 8; j++) {
      int currentBit = 1 & (currentChar >> j);
      if (currentBit == 1) {
        amountOf1s++;
      }
    }

    int parityBit = amountOf1s % 2; // Calcula a paridade: Se for ímpar é 1, se não é 0
    digitalWrite(pinClient, parityBit); 
    timeSkipper(); 

    digitalWrite(pinClient, 1); // Pino HIGH (Indica Final da transmissão)
    timeSkipper();

    Serial.print("Enviando o Caractere: ");
    Serial.println(currentChar);
    delay(1500);
  }
}
