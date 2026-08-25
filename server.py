from socket import *
serverPort = 12001
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('The server is ready to receive')

while True:
    connectionSocket, addr = serverSocket.accept()
    sentence = connectionSocket.recv(1024).decode()
    print("ORIGINAL =================")
    print(repr(sentence))
    print("FORMATADO =================")
    print(sentence)
    capitalizedSentence = sentence.upper()
    connectionSocket.send(capitalizedSentence.encode())
    connectionSocket.close()

def trata_mensagem(mensagem):
    splited = mensagem.upper().split('\r\n')
    metodo, url, versao = mensagem.split('\r\n')

    if metodo != 'GET':
        return "NÃO"
    




    
    