import socket
import struct
import zlib

# checksum function
def checksumFunc(data):
  checksumCalculated = zlib.crc32(data)
  return checksumCalculated

# configure environment
clientPort = 5000
clientAddress = "127.0.0.1"
serverPort = 5001
serverAddress = "127.0.0.1"

# create and bind the socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind((serverAddress, clientPort))

# get a message and convert it to bytes
content = str(input("Escreva sua mensagem: "))

while (content != "out"):
  # calculate checksum from message
  packageToBeSent = content.encode()
  checksumFromPackage = checksumFunc(packageToBeSent)
  print("checksum from message to be sent: " + str(checksumFromPackage) + "\n")

  # configure message header
  contentLength = len(packageToBeSent)
  udpHeader = struct.pack(
    "!IIII",
    clientPort,
    serverPort,
    contentLength,
    checksumFromPackage
  )

  # message to be sent
  packageWithHeader = udpHeader + packageToBeSent
  receiverAddress = (serverAddress, serverPort)
  client.sendto(packageWithHeader, receiverAddress)

  print("=======> message sent")

  # get returned message
  messageReceived, senderAddress = client.recvfrom(1024)
  contentReceived = messageReceived.decode()
  print("message received from server: " + contentReceived + "\n")

  content = str(input("Escreva sua mensagem: "))

client.close()
