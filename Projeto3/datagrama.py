class Head:
    messageType: str    # 'DD' - dados, 'HH' - handshake, '88' - verificação, '99' - mandar de novo
    senderId: str       # 'CC' - client, 'SS' - server
    receiverId: str     # 'CC' - client, 'SS' - server
    totalPayloads: str = '000000'
    currentPayloadIndex: str = '000000'
    payloadSize: str = '00'
    finalString = ''

    # Definindo o construtor
    def __init__(self, messageType, senderId, receiverId):
        self.messageType = messageType
        self.senderId = senderId
        self.receiverId = receiverId

    def payloadData(self, totalPayloads, currentPayloadIndex, payload):
        if self.messageType == 'DD':
            self.totalPayloads = str(totalPayloads)
            self.currentPayloadIndex = str(currentPayloadIndex)
            self.payloadSize = str(len(payload))
        else:
            raise Exception("Error: Message type does not support non-0 payload")

    def buildHead(self):
        while len(self.totalPayloads) < 6:
            self.totalPayloads = '0' + self.totalPayloads
        while len(self.currentPayloadIndex) < 6:
            self.currentPayloadIndex = '0' + self.currentPayloadIndex
        while len(self.payloadSize) < 2:
            self.payloadSize = '0' + self.payloadSize
        #self.currentPayloadIndex = '000000'
        #self.payloadSize = '00'
        self.finalString = self.messageType + self.senderId + self.receiverId + self.totalPayloads + self.currentPayloadIndex + self.payloadSize
        print(self.messageType, self.senderId, self.receiverId, self.totalPayloads, self.currentPayloadIndex, self.payloadSize)


class Datagrama:
    head: Head
    payload: str = ''
    EOP: str = 'ABC'

    def __init__(self, head, payload):
        self.head = head
        self.payload = payload