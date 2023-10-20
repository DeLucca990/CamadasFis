#include <Arduino.h>

int pinClient = 7;
byte msg = 0x0A; // letra A em hexadecimal
int msgBinary = int(msg);
float baudrate = 9600;

void setup() {
  pinMode(pinClient, OUTPUT);
  Serial.begin(baudrate); 
  digitalWrite(pinClient, HIGH); 
}

float timeSkipper(float skipTime=1, float baudrate=9600, float T0=0){
  double clock = 1 / (21 * pow(10, 6)); // tempo de 1 pulso do relógio (T = 1/frequência)
  double T = 1 / baudrate; // tempo entre cada pulso do relógio, em segundos
  int numberOfClocks = ceil(T / clock) + 1; // número de pulsos do relógio a esperar, arredondado para o inteiro mais próximo
  for (int i = 0; i < int(numberOfClocks * skipTime); i++){ asm("NOP"); } // aguarde o tempo especificado
}

void loop() {
  int amountOf1s = 0; // contador para a quantidade de uns na mensagem

  digitalWrite(pinClient, 0); // envie o bit de início
  timeSkipper(); // sempre chamado após o envio de um bit
  
  for (int i = 0; i < 8; i++){ // envie os 8 bits (1 byte) da mensagem
    int currentBit = 1 & (msgBinary >> i); // obtenha o bit atual da mensagem, começando pelo bit menos significativo
    digitalWrite(pinClient, currentBit); // envie o bit atual
    if (currentBit == 1){ amountOf1s++; } // conte a quantidade de uns na mensagem
    timeSkipper(); // sempre chamado após o envio de um bit
  }

  int parityBit = amountOf1s % 2; // se o resto for igual a 0, então é par, senão é ímpar
  digitalWrite(pinClient, parityBit); // envie o bit de paridade
  timeSkipper(); // sempre chamado após o envio de um bit

  digitalWrite(pinClient, 1); // envie o bit de parada
  timeSkipper(); // sempre chamado após o envio de um bit
  
  Serial.print("Caractere Enviado: ");
  Serial.println(msg, HEX); // imprima a mensagem enviada (em hexadecimal)
  delay(1500);
}
