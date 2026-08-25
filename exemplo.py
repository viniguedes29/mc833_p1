
from socket import *
import sys

serverSocket = socket(AF_INET, SOCK_STREAM)
serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('The server is ready to receive')


while True:
    #Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()
    try:
        message = connectionSocket.recv(1024).decode()
        print(message.upper().split('\r\n')[0].split())

        method, url, version = message.upper().split('\r\n')[0].split()

        if version != 'HTTP/1.1':
            connectionSocket.send('HTTP/1.1 505 HTTP Version Not Supported'.encode())
            continue


        if method != 'GET':
            connectionSocket.send('HTTP/1.1 501 Not Implemented'.encode())
            continue


        filename = url[1:0]
        connectionSocket.send('HTTP/1.1 204 No Content'.encode())
        # f = open(filename[1:])
        # outputdata = #Fill in start #Fill in end
        # #Send one HTTP header line into socket
        # #Fill in start
        # #Fill in end
        # #Send the content of the requested file to the client
        # for i in range(0, len(outputdata)):
        # connectionSocket.send(outputdata[i].encode())
        
    except Exception as erro:
        print(f'ERROOOU: {erro}' )
    finally:
        connectionSocket.send("\r\n".encode())
        connectionSocket.close()

serverSocket.close()
sys.exit()#Terminate the program after sending the corresponding data
