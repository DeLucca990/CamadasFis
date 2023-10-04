# Camadas Físicas da Computação
## Grupo 🙋‍♂️🙋‍♀️:
* Pedro De Lucca
* Maria Vitória

## Projetos
### Projeto Loopback [Projeto 1]

Esse software é capaz de :
1) Enviar uma imagem através da porta de comunicação serial.
2) Receber a imagem simultaneamente ao envio e salva-la como uma cópia. Para isso a recepção do Arduino(pino rx) deve estar curto-circuitada com o pino de transmissão (pino tx).

### Projeto Client-Server [Projeto 2]

Nesse projeto desenvolvemos duas aplicações distintas:
- Uma aplicação (client) que deverá enviar via transmissão serial UART uma sequência de comandos que poderiam, por exemplo, controlar o estado da outra aplicação (server). A sequência
deve ter entre 10 e 30 comandos, a ser determinada pelo client. O server não sabe a quantidade de comandos que irá receber.
- Após a recepção, uma outra aplicação (server) deverá retornar ao client uma mensagem informando o número de estados
que foram recebidos. Assim que o cliente receber a resposta com este número, poderá verificar se todos os estados
foram recebidos, e o processo termina.

### Projeto Datagrama [Projeto 3]

Para esse projeto modificamos o anterior para que todas as mensagens trocadas entre o servidor e o cliente sejam um datagrama completo. Isso significa que mesmo que queira enviar um único byte, deverá enviar um pacote
compondo um datagrama. Para isso vamos considerar o seguinte datagrama:
- HEAD – 12 BYTES - fixo
- PAYLOAD – variável entre 0 e 50 BYTES (pode variar de pacote para pacote)
- EOP – 3 BYTES – fixo (valores de sua livre escolha)

Além disso, para iniciar a comunicação entre o servidor e o cliente foi implementado o handshake que funciona da seguinte forma:

Antes do início do envio da mensagem, o cliente deve enviar uma mensagem para verificar se o server está
“vivo”, pronto para receber o arquivo a ser enviado. O server então deve responder como uma mensagem
informando que ele está pronto para receber. Enquanto a mensagem não seja recebida pelo cliente, este não
começa o envio de nada. Caso o cliente não receba a resposta do servidor dentro de 5 segundos, informando que
está pronto para receber o arquivo, o usuário recebe uma mensagem: “Servidor inativo. Tentar novamente? S/N”. Se
o usuário escolher “S”, outra mensagem de verificação é enviada ao server. Caso escolha não. Tudo se encerra.
Caso o servidor responda ao cliente em menos de 5 segundos, o cliente deve iniciar a transmissão do arquivo.

Por fim, é importante ressaltar que foi feita uma fragmentação do payload, isso porque o arquivo a ser enviado é maior que o tamanho do payload, por isso é preciso enviá-lo em pacotes, e todos os pacotes seguem a estrutura do datagrama descrito anteriormente. 

### Projeto Protocolo ponto a ponto [sem CRC: Projeto 4]

Para esse projeto implementamos uma aplicação para que a comunicação seja feita para sensores se comunicarem serialmente com padrão UART de
maneira segura, sem perda de dados. E essa comunicação deve ser feita para envio de arquivos para os servidores, sendo uma rotina
de envio executada pelo sensor toda vez que este tem um arquivo a ser enviado.
Além disso, a camada superior da comunicação deve funcionar seguindo
uma estratégia já definida, onde os arquivos são enviados em pacotes, respeitando o datagrama definido a seguir:

- h0 – tipo de mensagem
- h1 – id do sensor
- h2 – id do servidor
- h3 – número total de pacotes do arquivo
- h4 – número do pacote sendo enviado
- h5 – se tipo for handshake: id do arquivo, se tipo for dados: tamanho do payload.
- h6 – pacote solicitado para recomeço quando a erro no envio.
- h7 – último pacote recebido com sucesso.
- h8 – h9 – CRC
- PAYLOAD – variável entre 0 e 114 bytes. Reservado à transmissão dos arquivos.
- EOP – 4 bytes: \xAA\xBB\xCC\xDD

Por fim, existem 6 tipos de mensagens:

- TIPO 1 – Esta mensagem representa um chamado do cliente enviado ao servidor convidando-o para a transmissão.
- TIPO 2 – Essa mensagem é enviada pelo servidor ao cliente, após o primeiro receber uma mensagem tipo 1 com o número
identificador correto.
- TIPO 3 – A mensagem tipo 3 é a mensagem de dados. Este tipo de mensagem contém de fato um bloco do dado a ser enviado
(payload). 
- TIPO 4 – Essa mensagem é enviada do servidor para o cliente toda vez que uma mensagem tipo 3 é recebida pelo servidor e
averiguada.
- TIPO 5 – É uma mensagem de time out.
- TIPO 6 – É uma mensagem de erro. 

### Projeto Protocolo ponto a ponto [com CRC: Projeto 5]

Esse projeto utiliza tudo o que foi desenvolvido anteriormente com o acréscimo do CRC.

Sendo o CRC (Cyclic Redundancy Check) um algoritmo de verificação de integridade usado para detectar erros em dados durante a transmissão ou armazenamento. Ele é aplicado a um conjunto de dados e gera um valor de verificação (checksum) que é enviado juntamente com os dados. No código desenvolvido, o CRC é calculado usando a função `crccheck` para obter um valor de verificação de 2 bytes (h8 e h9). Esse valor é adicionado ao pacote como parte do cabeçalho, permitindo que o destinatário verifique se os dados foram recebidos corretamente. Se o valor CRC calculado no destino for diferente do valor recebido, isso indica a presença de erros nos dados transmitidos.