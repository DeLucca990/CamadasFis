#include <Arduino.h>

int pinServer = 5; // Número do pino usado pelo Arduino para receber dados
float baudrate = 9600; // 9600 bits por segundo
int msg;
bool startBitDetected = false; // Flag para detectar o início de um novo caractere

void setup() {
  pinMode(pinServer, INPUT); // Configura o pino digital como entrada, pois o servidor está recebendo do cliente
  Serial.begin(baudrate); // Inicia a porta serial, definindo a taxa de dados de recepção como 9600 bits por segundo
}

float timeSkipper(float skipTime = 1, float baudrate = 9600, float T0 = 0) {
  double clock = 1.0 / (21.0 * pow(10, 6)); // Tempo de um clock (T = 1/frequência), onde a frequência é de 21 MHz
  double T = 1.0 / baudrate; // Tempo entre cada clock, em segundos
  int numberOfClocks = floor(T / clock) + 1; // Número de clocks a aguardar, arredondado para o inteiro mais próximo
  for (int i = 0; i < int(numberOfClocks * skipTime); i++) {
    asm("NOP"); // Aguarde o tempo especificado
  }
}

void loop() {
  if (digitalRead(pinServer) == 0) {
    if (!startBitDetected) {
      timeSkipper(1.5); // Posiciona o momento para ler bits no meio de cada bit (portanto, o bit de início é ignorado)
      startBitDetected = true; // Marca o início de um novo caractere
    } else {
      int amountOf1s = 0;
      for (int i = 0; i < 8; i++) {
        int currentBit = digitalRead(pinServer); // Lê o bit atual
        timeSkipper(); // Sempre chamado após a leitura de um bit
        if (currentBit == 1) {
          amountOf1s++; // Conta a quantidade de bits 1 na mensagem
        }
        msg |= (currentBit << i); // Adicione o bit atual à mensagem
      }
      int parityBitReceived = digitalRead(pinServer); // Lê o bit de paridade recebido
      int parityBitCalculated = (amountOf1s % 2); // Calcula o bit de paridade a partir da mensagem enviada
      if (parityBitReceived == parityBitCalculated) { // Se o bit de paridade recebido for igual ao bit de paridade calculado, a mensagem está correta
        Serial.print("Caractere recebido: ");
        Serial.println(char(msg));
        Serial.println("Bit de paridade está correto");
      } else { // Se o bit de paridade recebido for diferente do bit de paridade calculado, a mensagem está incorreta
        Serial.println("ERRO. Bit de paridade não está correto");
      }
      msg = 0; // Limpa a variável da mensagem
      startBitDetected = false; // Marca o fim do caractere atual
      delay(1500);
    }
  }
}
