from audioop import add
import socket
import struct
import binascii

SEGMENT_SIZE = 16

def checksumCalculator(data):
  data = bin(int(binascii.hexlify(data),16))

  stPacket = data[0:16] or '0'
  ndPacket = data[16:32] or '0'
  rdPacket = data[32:48] or '0'
  thPacket = data[48:64] or '0'

  sum = bin(
    int(stPacket, 2) +
    int(ndPacket, 2) +
    int(rdPacket, 2) +
    int(thPacket, 2)
  )[2:]

  if(len(sum) > 16):
    x = len(sum)-16
    sum = bin(
      int(sum[0:x], 2) +
      int(sum[x:], 2)
    )[2:]

  if(len(sum) < 16):
    sum = '0' * (16 - len(sum)) + sum

  checksum = ''

  for i in sum:
    if(i == '1'):
      checksum += '0'
    else:
      checksum += '1'

  return checksum

def checkChecksumCalculator(dataToCalc, checksum):
  dataToCalc = bin(int(binascii.hexlify(dataToCalc), 16))

  checksum = bin(int(binascii.hexlify(bytes(checksum)), 16))

  stPacket = dataToCalc[0:16] or '0'
  ndPacket = dataToCalc[16:32] or '0'
  rdPacket = dataToCalc[32:48] or '0'
  thPacket = dataToCalc[48:64] or '0'

  receiverSum = bin(int(stPacket, 2)
    + int(ndPacket, 2)
    + int(checksum, 2)
    + int(rdPacket, 2)
    + int(thPacket, 2)
    + int(checksum, 2)
  )[2:]

  if(len(receiverSum) > 16):
    x = len(receiverSum) - 16

    receiverSum = bin(
      int(receiverSum[0:x], 2) +
      int(receiverSum[x:], 2)
    )[2:]

  return int(receiverSum, 2) == 0

with open('file-to-test.txt') as f:
  content = f.read()

sourcePort = 1111
destinationPort = 1112
receiverAddress = ('127.0.0.1', destinationPort)
address = ('127.0.0.1', sourcePort)

socketObject = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recvSock.bind(address)
recvSock.settimeout(1)

offset = 0
seq = 0

while offset < len(content):
  if offset + SEGMENT_SIZE > len(content):
    segment = content[offset:]
  else:
    segment = content[offset:offset + SEGMENT_SIZE]

  offset += SEGMENT_SIZE - seq

  ackReceived = False

  while not ackReceived:
    packet = (str(seq) + segment).encode()
    dataLength = len(packet)
    checksum = checksumCalculator(packet)
    udpHeader = struct.pack(
      '!IIIII',
      sourcePort,
      destinationPort,
      dataLength,
      int(checksum, 2),
      seq
    )

    packetWithHeader = udpHeader + packet

    socketObject.sendto(packetWithHeader, receiverAddress)

    try:
      message, address = recvSock.recvfrom(1024)

    except socket.timeout:
      print('Timeout')
    else:
      checksum = message[:16]
      ackSeq = message[19]
      if checksumCalculator(message[16:]) == checksum.decode() and chr(ackSeq) == str(seq):
        ackReceived = True

  seq = 1 - seq

socketObject.close()
