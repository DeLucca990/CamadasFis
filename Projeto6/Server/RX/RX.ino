#include <Arduino.h>

int pinServer = 7; 
float baudrate = 9600;
int msg;

void setup() {
  pinMode(pinServer, INPUT); 
  Serial.begin(baudrate);
}

float timeSkipper(float skipTime=1, float baudrate=9600, float T0=0){
  double clock = 1 / (21 * pow(10, 6)); // tempo de 1 pulso do clock (T = 1/frequência)
  double T = 1 / baudrate; // tempo entre cada pulso do clock, em segundos
  int numberOfClocks = floor(T / clock) + 1; // número de pulsos do relógio a esperar, arredondado para o inteiro mais próximo
  for (int i = 0; i < int(numberOfClocks * skipTime); i++){ asm("NOP"); } // aguarde o tempo especificado
}

void loop() {
  if (digitalRead(pinServer) == 0){
    int amountOf1s = 0;
    timeSkipper(1.5); // posicionando o momento de ler os bits no meio de cada bit (portanto, o bit de início é ignorado)
    for (int i = 0; i < 8){
      int currentBit = digitalRead(pinServer); // leia o bit atual
      timeSkipper(); // sempre chamado após ler um bit
      if (currentBit == 1){ amountOf1s++; } // conte a quantidade de uns na mensagem
      msg |= (currentBit << i); // adicione o bit atual à mensagem
    }
    int parityBitReceived = digitalRead(pinServer); // leia o bit de paridade recebido
    int parityBitCalculated = (amountOf1s % 2); // calcule o bit de paridade a partir da mensagem enviada
    if (parityBitReceived == parityBitCalculated){ // se o bit de paridade recebido for igual ao bit de paridade calculado, a mensagem está correta
      Serial.print("Dados recebidos: ");
      Serial.println(msg, HEX);
    } else { // se o bit de paridade recebido for diferente do bit de paridade calculado, a mensagem está incorreta
      Serial.println("ERRO. O bit de paridade NÃO está correto");
    }
    delay(1500);
  }
}
