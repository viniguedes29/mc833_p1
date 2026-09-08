from socket import *
from threading import Thread
import mimetypes

SERVER_PORT = 12000
BUFFER_SIZE = 1024

STATUS_MESSAGES = {
    200: "OK",
    400: "Bad Request",
    404: "Not Found",
    501: "Not Implemented",
    505: "HTTP Version Not Supported"
}


def receive_request(connection_socket):
    """
    Recebe os dados enviados pelo cliente e retorna
    a mensagem decodificada.

    A interpretação e validação da mensagem são realizadas
    posteriormente.
    """
    return connection_socket.recv(BUFFER_SIZE).decode()


def parse_request(message):
    """
    Interpreta a mensagem recebida como uma requisição HTTP
    e extrai somente as informações necessárias ao servidor:
    método, URL e versão HTTP.
    """
    request_line = message.split("\r\n", 1)[0]
    fields = request_line.split()

    if len(fields) != 3:
        return None

    method, url, version = fields

    return {
        "method": method.upper(),
        "url": url,
        "version": version.upper()
    }


def validate_request(request):
    """
    Verifica se a requisição possui um formato e características
    suportadas pelo servidor.

    Retorna None caso a requisição seja válida ou o código HTTP
    correspondente ao erro encontrado.
    """
    if request is None:
        return 400

    if request["version"] != "HTTP/1.1":
        return 505

    if request["method"] != "GET":
        return 501

    return None


def get_filename(request):
    """
    Obtém o nome do arquivo solicitado a partir da URL
    presente na requisição.
    """
    url = request["url"]

    if url == "/":
        return "index.html"

    return url[1:]


def read_file(filename):
    """
    Tenta abrir e ler o arquivo solicitado.

    O arquivo é aberto em modo binário para permitir o envio
    tanto de arquivos de texto quanto de imagens e outros
    tipos de conteúdo.
    """
    with open(filename, "rb") as file:
        return file.read()


def build_response(status_code, body=b"", content_type="text/plain"):
    """
    Constrói a mensagem de resposta HTTP a ser enviada
    ao cliente.
    """
    status_message = STATUS_MESSAGES[status_code]

    header = (
        f"HTTP/1.1 {status_code} {status_message}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Content-Type: {content_type}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    return header.encode() + body


def process_request(request):
    """
    Executa o processamento da requisição.

    O pipeline é composto pelas etapas:
        1. Validação da requisição;
        2. Identificação do arquivo solicitado;
        3. Leitura do arquivo;
        4. Construção da resposta HTTP.
    """

    error_code = validate_request(request)

    if error_code is not None:
        return build_response(error_code)

    filename = get_filename(request)

    try:
        content = read_file(filename)

    except FileNotFoundError:
        return build_response(404)

    content_type, _ = mimetypes.guess_type(filename)

    if content_type is None:
        content_type = "application/octet-stream"

    return build_response(
        200,
        body=content,
        content_type=content_type
    )


def handle_client(connection_socket, addr):
    """
    Realiza o atendimento de uma conexão.

    Recebe os dados do cliente, interpreta a requisição,
    processa seu conteúdo e envia a resposta correspondente.
    """
    print(f"Connection received from {addr}")

    try:
        message = receive_request(connection_socket)

        request = parse_request(message)

        response = process_request(request)

        connection_socket.sendall(response)

    except Exception as error:
        print(f"Error while serving {addr}: {error}")

    finally:
        connection_socket.close()
        print(f"Connection with {addr} closed")


def main():
    """
    Inicializa o servidor TCP e permanece aguardando
    conexões de clientes.
    """
    server_socket = socket(AF_INET, SOCK_STREAM)

    # Permite reutilizar a porta após reiniciar o servidor
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    server_socket.bind(("", SERVER_PORT))
    server_socket.listen(5)

    print(f"Server listening on port {SERVER_PORT}")

    try:
        while True:
            print("Ready to serve...")

            connection_socket, addr = server_socket.accept()
            client_thread = Thread(
                target=handle_client,
                args=(connection_socket, addr)
            )

            client_thread.start()

    except KeyboardInterrupt:
        print("\nServer interrupted.")

    finally:
        server_socket.close()


if __name__ == "__main__":
    main()