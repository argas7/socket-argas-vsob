import binascii
import socket
import struct
import zlib

def checkCalcChecksum(info, checksum):
   
    info = bin(int(binascii.hexlify(info),16))
    checksum = bin(int(binascii.hexlify(bytes(checksum)),16))

    c1 = info[0:16] or '0'
    c2 = info[16:32] or '0'
    c3 = info[32:48] or '0'
    c4 = info[48:64] or '0'
 
    ReceiverSum = bin(int(c1, 2)+int(c2, 2)+int(checksum, 2) +
                      int(c3, 2)+int(c4, 2)+int(checksum, 2))[2:]
 
    if(len(ReceiverSum) > 16):
        x = len(ReceiverSum)-16
        ReceiverSum = bin(int(ReceiverSum[0:x], 2)+int(ReceiverSum[x:], 2))[2:]
    if(len(ReceiverSum) < 16):
        ReceiverSum = '0'*(16-len(ReceiverSum))+ReceiverSum
 
    return int(ReceiverSum, 2) == 0

def calcVhecksum(info):

    info = bin(int(binascii.hexlify(info),16))
   
    c1 = info[0:16] or '0'
    c2 = info[16:32] or '0'
    c3 = info[32:48] or '0'
    c4 = info[48:64] or '0'
 
    Sum = bin(int(c1, 2)+int(c2, 2)+int(c3, 2)+int(c4, 2))[2:]

    if(len(Sum) > 16):
        x = len(Sum)-16
        Sum = bin(int(Sum[0:x], 2)+int(Sum[x:], 2))[2:]
    if(len(Sum) < 16):
        Sum = '0'*(16-len(Sum))+Sum
 
    Checksum = ''
    for i in Sum:
        if(i == '1'):
            Checksum += '0'
        else:
            Checksum += '1'
    return Checksum

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
    udpHeader = struct.unpack("!IIIII", udpHeader)
    correct_checksum = udpHeader[3]

    seq = udpHeader[4]
    content = info[1:]

    is_info_corrupted = checkCalcChecksum(info, correct_checksum)

    if not is_info_corrupted:
        value = "ACK" + str(seq)
        checksum = calcVhecksum(value.encode())
        socketSend.sendto((checksum + value).encode(), receiverAddr)
        if str(seq) == str(expecting_seq):
            print(content.decode())
            expecting_seq = 1 - expecting_seq
    else:
        negative_seq = 1 - expecting_seq
        checksum = calcVhecksum(negative_seq)
        header = struct.pack("!II", int(checksum, 2), negative_seq)
        socketSend.sendto(header, receiverAddr)
