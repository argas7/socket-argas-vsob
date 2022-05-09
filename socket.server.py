import binascii
import socket
import struct
import zlib

# chatbot classes ----------
class Item:
  def __init__(self, id, name, cost):
    self.id = id
    self.name = name
    self.cost = cost

class Menu:
  def __init__(self):
    self.items = [Item(1, 'Pizza', 10), Item(2, 'Burger', 5), Item(3, 'Fries', 3)]

  def getMenu(self):
    menu = ''
    for item in self.items:
      menu += str(item.id) + ' ' + item.name + ' ' + str(item.cost) + '\n'
    return menu


class Customer:
  def __init__(self, name, ip, port, table):
    self.name = name
    self.orders = []
    self.ip = ip
    self.port = port
    self.table = table
    self.seqNumber = 0
    self.serverState = 'WAITING'
    self.billToPay = 0


  def updateSeqNumber(self, updatedSeq):
    self.seqNumber = updatedSeq

  def getTotalCost(self):
    totalCost = 0
    for order in self.orders:
      totalCost += order.cost
    return totalCost

  def getIndividualBill(self):
    bill = '| ' + self.name + ' |' + '\n'
    for order in self.orders:
      bill += order.name + ': ' + str(order.cost) + '\n'
    bill += 'Total: ' + str(self.getTotalCost())
    return bill

  def makeOrder(self, menu, orderId):
    for item in menu.items:
      if item.id == orderId:
        self.orders.append(item)
        self.billToPay = self.billToPay + item.cost

  def payBill(self, valuePaid):
    self.billToPay = self.billToPay - valuePaid
    if(self.billToPay < 0):
      self.billToPay = 0



class CINtofome:
  def __init__(self):
    self.menu = Menu()
    self.customers = []

  def getTableBillToPay(self, table):
    bill = 0
    for customer in self.customers:
      if customer.table == table:
        bill += customer.billToPay  
    return bill

  def getTableBill(self, tableId):
    bill = ''
    for customer in self.customers:
      if customer.table == tableId:
        bill += customer.getIndividualBill() + '\n'
    bill += 'Total da mesa: ' + str(self.getTotalCost())
    return bill
    
  def customerExists(self, ip, port):
    for customer in self.customers:
      if customer.ip == ip and customer.port == port:
        return True
    return False

  def getCustomer(self, ip, port):
    for customer in self.customers:
      if customer.ip == ip and customer.port == port:
        return customer

  def removeCustomer(self, ip, port):
    for customer in self.customers:
      if customer.ip == ip and customer.port == port:
        self.customers.remove(customer)

  def getMessage(self, ip, port, message):
    if(not self.customerExists(ip, port)):
      self.customers.append(Customer(message, ip, port, 0))

    customer = self.getCustomer(ip, port)

    if customer.serverState == 'WAITING':
      if message == 'chefia':
        customer.serverState = 'Waiting table'
        return 'Digite sua mesa'
      return 'Erro'
    elif customer.serverState == 'Waiting table':
      customer.table = message
      customer.serverState = 'Waiting name'
      return 'Digite seu nome'
    elif customer.serverState == 'Waiting name':
      customer.name = message
      customer.serverState = 'Waiting option'
      returnMessage = ''
      returnMessage = returnMessage + 'Digite uma das opções a seguir (o número)' + '\n' + '\n'
      returnMessage = returnMessage + '1 - cardápio' + '\n'
      returnMessage = returnMessage + '2 - pedido' + '\n'
      returnMessage = returnMessage + '3 - conta individual' + '\n'
      returnMessage = returnMessage + '4 - conta da mesa' + '\n'
      returnMessage = returnMessage + '5 - pagar' + '\n'
      returnMessage = returnMessage + '6 - levantar'
      return returnMessage
    elif customer.serverState == 'Waiting option':
      if message == '1':
        customer.serverState = 'Waiting option'
        return self.menu.getMenu()
      elif message == '2':
        customer.serverState = 'Waiting order'
        return 'Digite qual o primeiro item que gostaria (número)'
      elif message == '3':
        customer.serverState = 'Waiting option'
        return customer.getIndividualBill()
      elif message == '4':
        customer.serverState = 'Waiting option'
        return self.getTableBill(customer.table)
      elif message == '5':
        customer.serverState = 'Waiting pay'
        return ('Sua conta foi R$ ' + str(customer.billToPay) + 'e a da mesa R$ ' + str(self.getTableBillToPay(customer.table)) + '. Digite o valor a ser pago')
      elif message == '6':
        customer.serverState = 'Waiting option'
        if customer.billToPay == 0:
          self.removeCustomer(ip, port)
          return 'volte sempre ^^'
        else:
          return 'Ainda faltam R$ ' + str(customer.billToPay) + 'da sua conta'
      return 'Erro'
    elif customer.serverState == 'Waiting order':
      customer.makeOrder(self.menu, int(message))
      customer.serverState = 'Waiting option'
      return 'Pedido feito'
    elif customer.serverState == 'Waiting pay':
      customer.payBill(int(message))
      customer.serverState = 'Waiting option'
      if(int(message) == customer.billToPay):
        return 'Pagamento realizado'
      elif(int(message) < customer.billToPay):
        return ('Pagamento realizado. Falta R$ ' + str(customer.billToPay))
      elif(int(message) > customer.billToPay):
        return 'Pagamento realizado. Vamos pegar o que sobrou como gorjeta. Muito obrigado!!'
      return 'Erro'
    return 'Erro'



# chatbot classes ----------

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

cintofomeServer = CINtofome()

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

  if not isInfoCorrupted:
    print(senderAddress[0])

    # extrair dados da mesagem:
    custumerAddress, custumerPort = senderAddress
    messageReceived = contentFromMessage.decode()

    # chamar cintofome handler
    messageToReturnToTheClient = cintofomeServer.getMessage(
      custumerAddress,
      custumerPort,
      messageReceived
    )

    value = 'ACK' + str(seqReceived)
    checksum = checksumCalculator(value.encode())
    serverSocket.sendto((checksum + value + messageToReturnToTheClient).encode(), clientAddress)

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
