
from socket import *
import sys

serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
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

        method, url, version = message.split('\r\n')[0].split()

        if version.upper() != 'HTTP/1.1':
            connectionSocket.send('HTTP/1.1 505 HTTP Version Not Supported\r\n'.encode())
            continue


        if method.upper() != 'GET':
            connectionSocket.send('HTTP/1.1 501 Not Implemented\r\n'.encode())
            continue


        filename = url[1:]
        print(filename[-4:])
        if filename == '':
            connectionSocket.send('HTTP/1.1 204 No Content\r\n'.encode())
        elif filename[-4:] == '.ico':
            f = open(filename, 'rb')
            outputdata = f.read()
            connectionSocket.send(f'HTTP/1.1 200 OK\r\n Content-Length: {len(outputdata)}\r\n\r\n'.encode())
            connectionSocket.sendall(outputdata)

        else:
            f = open(filename)
            outputdata = f.read()
            
            connectionSocket.send(f'HTTP/1.1 200 OK\r\n Content-Length: {len(outputdata)}\r\n\r\n'.encode())

            for i in range(0, len(outputdata)):
                connectionSocket.send(outputdata[i].encode())
        
    except Exception as erro:
        print(f'ERROOOU: {erro}' )
        connectionSocket.send('HTTP/1.1 404 Not Found\r\n'.encode())
    finally:
        connectionSocket.send("\r\n".encode())
        connectionSocket.close()

serverSocket.close()
sys.exit()#Terminate the program after sending the corresponding data
