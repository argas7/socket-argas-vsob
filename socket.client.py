import binascii
import socket
import struct
import zlib

def checkCalcChecksum(info, checksum):
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

def calcChecksum(info):
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

portSrc = 1112
portDst = 1111
receiverAddr = ('127.0.0.1', portDst)
mtAddr = ('127.0.0.1', portSrc)

socketSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sockRcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockRcv.bind(mtAddr)

expecting_seq = 0

while True:
  fullPacket, senderAddress = sockRcv.recvfrom(1024)

  udpHeader = fullPacket[:20]
  info = fullPacket[20:]
  udpHeader = struct.unpack('!IIIII', udpHeader)
  correct_checksum = udpHeader[3]

  seq = udpHeader[4]
  content = info[1:]

  is_info_corrupted = checkCalcChecksum(info, correct_checksum)

  if not is_info_corrupted:
    value = 'ACK' + str(seq)
    checksum = calcChecksum(value.encode())
    socketSend.sendto((checksum + value).encode(), receiverAddr)

    if str(seq) == str(expecting_seq):
      print(content.decode())
      expecting_seq = 1 - expecting_seq
    else:
      negative_seq = 1 - expecting_seq
      checksum = calcChecksum(negative_seq)
      header = struct.pack('!II', int(checksum, 2), negative_seq)
      socketSend.sendto(header, receiverAddr)
