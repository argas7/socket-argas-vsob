import socket
import struct
import zlib
import binascii

SEGMENT_SIZE = 16

def checksumCalculatorCheckFunc(info, checksum):
  info = bin(int(binascii.hexlify(info), 16))
  checksum = bin(int(binascii.hexlify(bytes(checksum)), 16))

  stPacket = info[0:16] or '0'
  ndPacket = info[16:32] or '0'
  rePacket = info[32:48] or '0'
  thPacket = info[48:64] or '0'

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

def checksumCalculator(info):
  info = bin(int(binascii.hexlify(info),16))

  stPacket = info[0:16] or '0'
  ndPacket = info[16:32] or '0'
  rePacket = info[32:48] or '0'
  thPacket = info[48:64] or '0'

  binarySum = bin(
    int(stPacket, 2) +
    int(ndPacket, 2) +
    int(rePacket, 2) +
    int(thPacket, 2)
  )[2:]

  if(len(binarySum) > 16):
    x = len(binarySum)-16

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
clientAddress = "127.0.0.1"
serverPort = 5001
serverAddress = "127.0.0.1"

expectingSeq = 0

# create and bind the socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((serverAddress, serverPort))
print("=======> socket is on to receive messages:\n")

while(True):
  entirePackage, senderAddress = server.recvfrom(1024)
  print("=======> socket received a message:")

  # destruct message received
  udpHeader = entirePackage[:20]
  receivedContent = entirePackage[20:]

  # unpack header
  udpHeader = struct.unpack("!IIIII", udpHeader)
  correctChecksum = udpHeader[3]

  # print if message is corrupted
  isContentCorrupted = checksumCalculatorCheckFunc(receivedContent, correctChecksum)

  seq = udpHeader[4]
  content = receivedContent[1:]

  if not isContentCorrupted:
    print("the data is not corrupted!")
    value = 'ACK' + str(seq)
    checksum = checksumCalculator(value.encode())
    server.sendto((checksum + value).encode(), (clientAddress, clientPort))

    if str(seq) == str(expectingSeq):
      print(content.decode())
      expectingSeq = 1 - expectingSeq
    else:
      print("the data was corrupted!")
      negativeSeq = 1 - expectingSeq
      checksum = checksumCalculator(negativeSeq)
      header = struct.pack('!II', int(checksum, 2), negativeSeq)
      server.sendto(header, (clientAddress, clientPort))

  # messageReceived = receivedContent.decode()
  # print("message received: " + messageReceived + "\n")

  # messageToBeReturned = messageReceived.encode()
  # server.sendto(messageToBeReturned, senderAddress)
