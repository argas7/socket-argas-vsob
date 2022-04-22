import socket
import struct
import zlib

#checksum function
def checksumFunc(data):
  checksumCalculated = zlib.crc32(data)
  return checksumCalculated

# configure environment
clientPort = 5000
clientAddress = "127.0.0.1"
serverPort = 5001
serverAddress = "127.0.0.1"

# create and bind the socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((serverAddress, serverPort))
print("=======> socket is on to receive messages:\n")

while(True):
  entirePackage, senderAddress = server.recvfrom(1024)
  print("=======> socket received a message:")

  # destruct message received
  udpHeader = entirePackage[:16]
  receivedContent = entirePackage[16:]

  # unpack header
  udpHeader = struct.unpack("!IIII", udpHeader)
  correctChecksum = udpHeader[3]

  # calculate checksum from message received and compare it with checksum received
  checksumFromMessageReceived = checksumFunc(receivedContent)

  # print if message is corrupted
  isContentCorrupted = correctChecksum != checksumFromMessageReceived
  print("checksum received: " + str(correctChecksum))
  print("checksum calculated: " + str(checksumFromMessageReceived))

  if (isContentCorrupted):
    print("the data was corrupted!")
  else:
    print("the data is not corrupted!")

  messageReceived = receivedContent.decode()
  print("message received: " + messageReceived + "\n")

  messageToBeReturned = messageReceived.encode()
  server.sendto(messageToBeReturned, senderAddress)
