import socket
import struct
import zlib
import binascii

SEGMENT_SIZE = 16

# checksum function
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
    x = len(sum) - 16
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

# configure environment
clientPort = 5000
clientAddress = "127.0.0.1"
serverPort = 5001
serverAddress = "127.0.0.1"

# create and bind the socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind((serverAddress, clientPort))

offset = 0
seq = 0

# get a message and convert it to bytes
content = str(input())

while (content != "levantar"):
  # packageWithHeader, receiverAddress = prepareMessageToBeSent(content)
  # send the message and start timer
  client.settimeout(1)

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
        clientPort,
        serverPort,
        dataLength,
        int(checksum, 2),
        seq
      )

      packetWithHeader = udpHeader + packet
      receiverAddress = (serverAddress, serverPort)

      client.sendto(packetWithHeader, receiverAddress)

      try:
        message, address = client.recvfrom(1024)
      except socket.timeout:
        print('Timeout')
      else:
        checksum = message[:16]
        ackSeq = message[19]
        if checksumCalculator(message[16:]) == checksum.decode() and chr(ackSeq) == str(seq):
          ackReceived = True

    seq = 1 - seq

  print("=======> message sent")

  # get returned message
  messageReceived, senderAddress = client.recvfrom(1024)
  print("message received from server: " + messageReceived + "\n")

  content = str(input("Escreva sua mensagem: "))

client.close()
