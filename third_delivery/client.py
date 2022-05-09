from audioop import add
import socket
import struct
import binascii

SEGMENT_SIZE = 16

def checksumCalculator(message):
  message = bin(int(binascii.hexlify(message), 16))

  stPacket = message[0:16] or '0'
  ndPacket = message[16:32] or '0'
  rdPacket = message[32:48] or '0'
  thPacket = message[48:64] or '0'

  binarySum = bin(
    int(stPacket, 2) +
    int(ndPacket, 2) +
    int(rdPacket, 2) +
    int(thPacket, 2)
  )[2:]

  if(len(binarySum) > 16):
    x = len(binarySum) - 16

    binarySum = bin(
      int(binarySum[0:x], 2) +
      int(binarySum[x:], 2)
    )[2:]

  if(len(binarySum) < 16):
    binarySum = '0' * (16 - len(binarySum)) + binarySum

  checksum = ''

  for i in binarySum:
    if(i == '1'):
      checksum += '0'
    else:
      checksum += '1'

  return checksum

# configure environment
clientPort = 5000
serverPort = 5001

serverAddress = ('127.0.0.1', serverPort)
clientAddress = ('127.0.0.1', clientPort)

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.bind(clientAddress)

currSEQ = 0
connectionStatus = "started"

while(not (connectionStatus == "closed")):
  print("Waiting for message to send")
  content = str(input())
  offset = 0

  clientSocket.settimeout(1)
  while offset < len(content):
    if offset + SEGMENT_SIZE > len(content):
      segment = content[offset:]
    else:
      segment = content[offset:offset + SEGMENT_SIZE]

    offset += SEGMENT_SIZE - currSEQ

    ackReceived = False

    while(not ackReceived):
      packet = (str(currSEQ) + segment).encode()
      dataLength = len(packet)
      checksum = checksumCalculator(packet)
      udpHeader = struct.pack(
        '!IIIII',
        clientPort,
        serverPort,
        dataLength,
        int(checksum, 2),
        currSEQ
      )

      packetWithHeader = udpHeader + packet

      clientSocket.sendto(packetWithHeader, serverAddress)

      try:
        message, serverFromAddress = clientSocket.recvfrom(1024)

      except socket.timeout:
        print('Timeout')
      else:
        checksum = message[:16]
        ackSeq = message[19]
        messageReceivedFromServer = message[20:]

        if (messageReceivedFromServer.decode() == "volte sempre ^^"):
          connectionStatus = "closed"

        if (checksumCalculator(message[16:20]) == checksum.decode() and chr(ackSeq) == str(currSEQ)):
          ackReceived = True

    currSEQ = 1 - currSEQ

clientSocket.close()
