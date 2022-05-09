import binascii
import socket
import struct
import zlib

def checksumCalculator(message):
  message = bin(int(binascii.hexlify(message), 16))

  stPacket = message[0:16] or '0'
  ndPacket = message[16:32] or '0'
  rePacket = message[32:48] or '0'
  thPacket = message[48:64] or '0'

  binarySum = bin(
    int(stPacket, 2) +
    int(ndPacket, 2) +
    int(rePacket, 2) +
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

def checksumChecker(message, checksum):
  message = bin(int(binascii.hexlify(message), 16))
  checksum = bin(int(binascii.hexlify(bytes(checksum)), 16))

  stPacket = message[0:16] or '0'
  ndPacket = message[16:32] or '0'
  rePacket = message[32:48] or '0'
  thPacket = message[48:64] or '0'

  receiverSum = bin(
    int(stPacket, 2) +
    int(ndPacket, 2) +
    int(checksum, 2) +
    int(rePacket, 2) +
    int(thPacket, 2) +
    int(checksum, 2)
  )[2:]

  if(len(receiverSum) > 16):
    x = len(receiverSum) - 16
    receiverSum = bin(
      int(receiverSum[0:x], 2) +
      int(receiverSum[x:], 2)
    )[2:]

  if(len(receiverSum) < 16):
    receiverSum = '0' * (16 - len(receiverSum)) + receiverSum

  return int(receiverSum, 2) == 0

# configure environment
clientPort = 5000
serverPort = 5001

# Só usando isso aqui pra testar, a gente pode salvar esses clients
# |__ dentro da estrutura de dados do CIntofome
clientAddress = ('127.0.0.1', clientPort)
serverAddress = ('127.0.0.1', serverPort)

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(serverAddress)

expectingSeq = 0

while True:
  fullPacket, senderAddress = serverSocket.recvfrom(1024)

  udpHeader = fullPacket[:20]
  message = fullPacket[20:]
  udpHeader = struct.unpack('!IIIII', udpHeader)
  checksumReceived = udpHeader[3]

  seqReceived = udpHeader[4]
  contentFromMessage = message[1:]

  isInfoCorrupted = checksumChecker(message, checksumReceived)

  print("========================> Received some message" + contentFromMessage.decode())
  if not isInfoCorrupted:
    print(senderAddress[0])
    # Escrever aqui os métodos do CIntofome
    # ...

    value = 'ACK' + str(seqReceived)
    checksum = checksumCalculator(value.encode())
    serverSocket.sendto((checksum + value + "").encode(), clientAddress)

    print('SEQ Received = ' + str(seqReceived))
    print('SEQ Esperado = ' + str(expectingSeq))
    if str(seqReceived) == str(expectingSeq):
      print(contentFromMessage.decode())
      expectingSeq = 1 - expectingSeq
    else:
      negativeSeq = 1 - expectingSeq
      checksum = checksumCalculator(str(negativeSeq))
      header = struct.pack('!II', int(checksum, 2), negativeSeq)
      serverSocket.sendto(header, clientAddress)
