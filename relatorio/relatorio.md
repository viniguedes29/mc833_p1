# Introdução

Este trabalho tem como objetivo o desenvolvimento de um servidor Web em Python capaz de receber e processar requisições HTTP GET utilizando sockets TCP. O servidor deve interpretar as requisições enviadas por clientes, localizar os arquivos solicitados no sistema de arquivos local e retornar respostas HTTP adequadas, incluindo respostas de sucesso (`200 OK`) e de recurso não encontrado (`404 Not Found`). Além disso, a aplicação deve ser capaz de atender múltiplos clientes simultaneamente por meio de um modelo concorrente baseado em threads.

A implementação foi desenvolvida a partir dos conceitos de programação em redes apresentados nas aulas, nos materiais disponibilizados e em pesquisas na internet. O servidor foi implementado em Python no arquivo `server.py`, tomando como base o modelo de servidor TCP nas instruções do laboratório e na implementação do livro texto. Para atender ao requisito de concorrência do projeto, esse modelo foi estendido com o uso de threads, de modo que cada conexão seja atendida independentemente enquanto a thread principal permanece disponível para aceitar novas conexões.

A organização do código priorizou legibilidade, modularidade e facilidade de compreensão. Para isso, as diferentes responsabilidades do servidor foram divididas em etapas bem definidas, como o recebimento dos dados pelo socket, a interpretação e validação da requisição, a identificação e leitura do recurso solicitado e a construção da resposta HTTP. Essa organização também busca facilitar a descrição e a análise de cada etapa ao longo deste relatório. Por se tratar de uma implementação de caráter didático, foram priorizados os requisitos propostos e os conceitos abordados na disciplina, sem a pretensão de reproduzir todos os mecanismos de robustez, segurança e otimização encontrados em servidores Web reais destinados a ambientes de produção. Por isso, não foram implementadas tratativas que vão além do escopo definido pelas orientações do laboratório.

Os testes apresentados neste trabalho serão realizados utilizando o navegador [NOME DO NAVEGADOR], versão [VERSÃO], disponível nos computadores do laboratório. A especificação do navegador e de sua versão é relevante, pois diferenças na forma como cada navegador constrói e envia requisições HTTP podem influenciar o comportamento observado durante os testes.

# Hipóteses e decisões de projeto

Para delimitar o comportamento esperado do servidor e manter a implementação compatível com o escopo proposto para o projeto, foram adotadas algumas hipóteses e decisões de projeto.

O servidor considera apenas requisições que utilizem o protocolo **HTTP/1.1** e o método **GET**. Além disso, o programa foi desenvolvido considerando requisições HTTP com estrutura válida e previsível, como aquelas produzidas pelos navegadores utilizados durante os testes. Requisições malformadas, que utilizem outros métodos HTTP ou versões diferentes do protocolo não fazem parte do funcionamento esperado da aplicação. Alguns desses casos foram mapeados para respostas HTTP específicas, indicando que a requisição, a operação ou a versão do protocolo não é suportada.

Os recursos solicitados pelo cliente correspondem a arquivos disponíveis localmente no diretório de execução do servidor. Quando o cliente realiza uma requisição para a raiz (`/`), considera-se que o recurso solicitado é o arquivo `index.html`.

Cada conexão TCP é utilizada para o atendimento de uma requisição e encerrada após o envio da respectiva resposta HTTP. Dessa forma, não foi implementado o mecanismo de conexões persistentes do HTTP/1.1.

Considera-se também que a requisição HTTP enviada pelo cliente pode ser recebida integralmente utilizando o buffer definido pela aplicação, de **1024 bytes**. Assim, o servidor realiza uma única operação de recebimento para obter os dados necessários à interpretação da requisição. Essa simplificação é suficiente para os casos de teste previstos neste trabalho, mas não contempla situações em que a requisição seja maior que o buffer ou seja recebida de forma fragmentada em múltiplas operações de leitura do socket.

Os arquivos solicitados são lidos em modo binário, permitindo que o servidor envie tanto arquivos de texto quanto imagens e outros tipos de conteúdo. O tipo MIME do recurso é determinado a partir da extensão do arquivo e incluído no cabeçalho `Content-Type` da resposta. Caso o tipo do arquivo não possa ser identificado, é utilizado como fallback o tipo genérico `application/octet-stream`. Para os arquivos disponibilizados como parte do Servidor Web utilizado nos testes, espera-se que seus respectivos tipos MIME possam ser identificados normalmente.

Por se tratar de uma implementação de caráter didático, foram priorizados os requisitos definidos para o projeto e os conceitos abordados na disciplina. Dessa forma, não foram implementados mecanismos adicionais de segurança, robustez, otimização ou compatibilidade que ultrapassem o escopo estabelecido para o trabalho.

# Descrição geral e casos de uso

O funcionamento do servidor foi organizado de forma modular, com cada etapa do processamento sendo atribuída a uma função específica. De maneira geral, a aplicação inicia e configura um socket TCP, permanece aguardando conexões de clientes e, a cada nova conexão recebida, cria uma thread responsável por realizar o atendimento daquele cliente. A partir dessa thread, a mensagem recebida pela conexão é processada pelo servidor. Inicialmente, os dados são recebidos pelo socket e interpretados de acordo com a estrutura esperada para uma requisição HTTP. Em seguida, são realizadas as etapas de validação da mensagem, identificação do recurso solicitado, leitura do arquivo correspondente e construção e envio da resposta ao cliente.

A rotina `main()` é responsável pela inicialização do servidor e pelo controle do fluxo principal da aplicação. Seu funcionamento pode ser dividido em duas etapas: a inicialização e configuração do socket do servidor e o laço responsável por aceitar conexões e criar as threads de atendimento.

## Inicialização e configuração do servidor

A execução do servidor é iniciada pela criação de um socket TCP utilizando a família de endereços `AF_INET` e o tipo `SOCK_STREAM`. A primeira opção indica a utilização de endereços IPv4, enquanto a segunda especifica o uso de um socket orientado a conexão, correspondente ao protocolo TCP.

```python
server_socket = socket(AF_INET, SOCK_STREAM)
```

Em seguida, é configurada a opção `SO_REUSEADDR` no socket do servidor:

```python
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
```

Essa configuração permite que o endereço e a porta utilizados pelo servidor possam ser reutilizados após sua interrupção e reinicialização. Dessa forma, evita-se que uma nova execução do programa seja temporariamente impedida porque o sistema operacional ainda mantém informações associadas à execução anterior.

Após essa configuração, o socket é associado à porta definida pela constante `SERVER_PORT`:

```python
server_socket.bind(("", SERVER_PORT))
```

O endereço vazio passado ao método `bind()` faz com que o servidor aceite conexões destinadas a qualquer uma das interfaces de rede disponíveis na máquina. A porta utilizada é definida previamente pela aplicação, permitindo que os clientes saibam em qual porta devem estabelecer a conexão TCP.

Em seguida, o socket é colocado em modo de escuta por meio do método `listen()`:

```python
server_socket.listen(5)
```

A partir desse momento, o socket passa a estar preparado para receber solicitações de conexão. O valor `5` define o tamanho máximo da fila de conexões pendentes que podem aguardar até serem aceitas pela aplicação.

Por fim, uma mensagem é exibida no terminal para indicar que a inicialização foi concluída e que o servidor está pronto para receber conexões:

```python
print(f"Server listening on port {SERVER_PORT}")
```

## Laço de atendimento e criação de threads

Após a configuração do socket, o servidor entra em um laço de execução contínua. Esse laço representa a rotina principal de atendimento e permanece ativo enquanto o programa estiver em execução.

```python
while True:
    print("Ready to serve...")

    connection_socket, addr = server_socket.accept()
```

A chamada ao método `accept()` bloqueia a execução da thread principal até que um cliente estabeleça uma nova conexão TCP. Quando uma conexão é aceita, são obtidos dois valores: `connection_socket`, que representa um novo socket utilizado exclusivamente para a comunicação com aquele cliente, e `addr`, que contém as informações de endereço do cliente conectado.

O socket `server_socket` continua sendo utilizado somente para receber novas conexões. O atendimento da conexão recém-estabelecida é delegado ao novo socket retornado por `accept()`.

Para permitir o atendimento simultâneo de múltiplos clientes, uma nova thread é criada para cada conexão aceita:

```python
client_thread = Thread(
    target=handle_client,
    args=(connection_socket, addr)
)

client_thread.start()
```

A função `handle_client` é definida como alvo da thread e recebe como argumentos o socket da conexão e o endereço do cliente. A chamada ao método `start()` inicia a execução da nova thread, que passa a realizar de forma independente todo o processamento relacionado àquela conexão.

Dessa maneira, a thread principal não precisa aguardar o término do atendimento do cliente atual. Logo após iniciar a nova thread, ela retorna ao início do laço e executa novamente `accept()`, ficando disponível para receber outras conexões. Assim, diferentes clientes podem ser atendidos simultaneamente por threads distintas.

De forma simplificada, o fluxo executado pela rotina principal pode ser representado como:

```text
Inicialização do servidor
        |
        v
Criação e configuração do socket
        |
        v
     listen()
        |
        v
     accept()
        |
        +------> nova thread ---> handle_client()
        |
        v
     accept()
        |
        +------> nova thread ---> handle_client()
        |
       ...
```

O laço é executado dentro de um bloco `try`, permitindo que o servidor seja interrompido manualmente por meio de uma exceção `KeyboardInterrupt`. Nesse caso, a interrupção é informada no terminal e, independentemente da forma como o laço seja encerrado, o bloco `finally` garante o fechamento do socket principal do servidor.

```python
except KeyboardInterrupt:
    print("\nServer interrupted.")

finally:
    server_socket.close()
```

Essa organização mantém separadas as responsabilidades da aplicação: a thread principal fica responsável exclusivamente por aceitar novas conexões, enquanto as threads criadas ficam responsáveis pelo atendimento individual de cada cliente.

## Rotina de atendimento ao cliente

Após a criação de uma thread para uma nova conexão, a execução do atendimento é transferida para a função `handle_client()`. Essa função atua como ponto de entrada para todo o processamento associado a um cliente específico, recebendo como parâmetros o socket criado exclusivamente para aquela conexão e o endereço do cliente.

A rotina foi organizada como um **pipeline de processamento**, no qual a saída de uma etapa é utilizada como entrada da etapa seguinte. Dessa forma, `handle_client()` não concentra toda a lógica necessária para interpretar e responder à mensagem recebida. Em vez disso, ela coordena a execução de funções menores, cada uma responsável por uma etapa específica do atendimento.

O fluxo geral realizado pela função pode ser representado da seguinte forma:

```text
Conexão estabelecida
        |
        v
Recebimento da mensagem
   (receive_request)
        |
        v
Interpretação da mensagem
    (parse_request)
        |
        v
Processamento da solicitação
   (process_request)
        |
        v
Envio da resposta
      (sendall)
        |
        v
Fechamento da conexão
```

Inicialmente, `receive_request()` obtém os dados enviados pelo cliente por meio do socket. A mensagem recebida é então encaminhada para `parse_request()`, responsável por interpretar sua estrutura e extrair as informações necessárias para as etapas seguintes. O resultado dessa interpretação é passado para `process_request()`, que concentra o processamento da solicitação, incluindo sua validação, a identificação e leitura do recurso solicitado e a construção da resposta correspondente. Por fim, a resposta produzida é enviada ao cliente através do método `sendall()`.

Essa organização permite que `handle_client()` funcione principalmente como uma função de **coordenação do fluxo de atendimento**, enquanto as responsabilidades específicas permanecem isoladas em outras rotinas. Além de tornar o código mais legível, essa divisão facilita a análise individual de cada etapa e evita que detalhes de interpretação, acesso a arquivos e construção de respostas sejam concentrados em uma única função.

Todo esse fluxo é executado dentro da thread criada para a conexão correspondente. Assim, eventuais operações realizadas durante o atendimento de um cliente não impedem que a thread principal do servidor continue aceitando novas conexões. Ao término do processamento, independentemente de seu resultado, o socket associado ao cliente é fechado no bloco `finally`, encerrando a conexão utilizada por aquela thread.

### Recebimento da mensagem

A primeira etapa do pipeline de atendimento é realizada pela função `receive_request()`, responsável por receber os dados enviados pelo cliente através do socket associado à conexão.

```python
def receive_request(connection_socket):
    """
    Recebe os dados enviados pelo cliente e retorna a mensagem decodificada.

    A interpretação e validação da mensagem são  realizadas posteriormente.
    """
    return connection_socket.recv(BUFFER_SIZE).decode()
```

A função recebe como parâmetro `connection_socket`, que corresponde ao socket criado especificamente para a comunicação com o cliente atendido pela thread atual. Sobre esse socket é executado o método `recv()`, que realiza a leitura dos dados disponíveis na conexão.

O valor máximo recebido em uma única chamada é definido pela constante `BUFFER_SIZE`, configurada como `1024` bytes. Dessa forma, nesta implementação, considera-se que os dados necessários para o processamento da mensagem podem ser obtidos por meio de uma única operação de leitura com o tamanho do buffer. 

Como nessa implementação somente é necessário capturar as informações da "request line", estou supondo que toda os bytes necessários podem ser lidos com apenas uma operação de leitura. Nos testes realizados não houve nenhum erro relacionado à necessidade de fazer mais de uma conexão.

![Estrutura da mensagem HTTP](img/image.png)

Como o método `recv()` retorna os dados no formato de bytes, é utilizado o método `decode()` para convertê-los em uma string antes de encaminhá-los para a próxima etapa do pipeline.

É importante destacar que essa função possui somente a responsabilidade de **receber e decodificar os dados**. Nenhuma interpretação ou validação da estrutura da mensagem é realizada nesse momento. O conteúdo retornado é posteriormente encaminhado para a rotina `parse_request()`, responsável por analisar sua estrutura e extrair as informações utilizadas pelo servidor. Essa rotina e as seguintes serão responsáveis por lidar com e tratar a mensagem traduzida na rotina `receive_request()`

### Interpretação da mensagem

Após o recebimento e a decodificação dos dados enviados pelo cliente, a próxima etapa do pipeline é realizada pela função `parse_request()`. Sua responsabilidade é interpretar a mensagem recebida de acordo com a estrutura esperada para uma requisição HTTP e extrair apenas as informações necessárias para o restante do processamento.

```python
def parse_request(message):
    """
    Interpreta a mensagem recebida como uma requisição HTTP e extrai somente as informações necessárias ao servidor:
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
```

Como visto anteriorment, uma requisição HTTP possui uma linha inicial, chamada request line, que contém o método utilizado, o recurso solicitado e a versão do protocolo. Como essas são as únicas informações necessárias para o processamento realizado pelo servidor, a primeira operação da função consiste em isolar essa linha da mensagem completa recebida.

```python
request_line = message.split("\r\n", 1)[0]
```

A sequência `\r\n` representa o final de uma linha na mensagem HTTP. O parâmetro 1 utilizado em `split()` limita a divisão à primeira ocorrência, de forma que apenas a primeira linha da mensagem seja separada do restante dos cabeçalhos. Por exemplo, a partir de uma requisição como:

```text
GET /index.html HTTP/1.1
Host: 143.106.16.12:12000
User-Agent: Mozilla/5.0
...
```

A variável `request_line` passa a conter somente:

```text
GET /index.html HTTP/1.1
```

Em seguida, essa linha é dividida utilizando os espaços como separadores:
```python
fields = request_line.split()
```
Para uma requisição no formato esperado, são obtidos exatamente três campos:
```text
GET /index.html HTTP/1.1
 |        |        |
 |        |        +--> versão HTTP
 |        +-----------> URL do recurso
 +--------------------> método HTTP
 ```

 Quando a mensagem possui o formato esperado, os três valores são armazenados nas variáveis `method`, `url` e `version`. Em seguida, é construída uma estrutura do tipo dicionário contendo essas informações:
```python
 {
    "method": method.upper(),
    "url": url,
    "version": version.upper()
}
```

Gerando a partir de `GET /index.html HTTP/1.1`:
```python
{
    "method": "GET",
    "url": "/index.html",
    "version": "HTTP/1.1"
}
```

Esta estapa não realiza validações de conteúdo. Caso não haja os 3 campos de interesse na primeira linha da requisição, retorna `None`.

Essa representação é utilizada pelas etapas seguintes do pipeline, permitindo que o restante da aplicação trabalhe diretamente com os campos relevantes da requisição, sem precisar interpretar novamente a mensagem HTTP original.

# Testes e execução

Os testes da aplicação foram realizados no laboratório IC-300, utilizando duas máquinas distintas da rede do Instituto de Computação. O servidor foi executado na máquina `beatles`, com endereço IP `143.106.16.12`, enquanto o cliente foi executado na máquina `sabbath`, com endereço IP `143.106.16.13`.

Na máquina servidor, a aplicação foi iniciada por meio do comando:

```bash
python3 server.py
```

A partir da máquina cliente, o servidor foi acessado através do navegador Firefox 154.0, utilizando o endereço IP da máquina servidor e a porta definida pela aplicação. O acompanhamento das requisições realizadas pelo navegador foi feito por meio das Ferramentas do Desenvolvedor, na aba Rede (Network), que permite visualizar as requisições HTTP enviadas pelo cliente e as respostas recebidas do servidor.

A figura abaixo apresenta um exemplo desse monitoramento durante a execução dos testes, exibindo as requisições realizadas para os recursos `index.html` e `favicon.ico`.

![Opções do desenvolvedor para monitorar o cliente](img/opcoes-desenvolvedor.png)

Durante o acesso à página inicial do servidor, o navegador realizou uma requisição semelhante à seguinte:

```text
GET / HTTP/1.1
Host: 143.106.16.12:12000
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Priority: u=0, i
```

Esse exemplo permite observar a estrutura da mensagem recebida pelo servidor. Apesar de diversos cabeçalhos serem enviados pelo navegador, a implementação utiliza apenas as informações presentes na primeira linha da requisição: o método HTTP, a URL solicitada e a versão do protocolo. Nesse caso, esses valores correspondem, respectivamente, a GET, / e HTTP/1.1.

Como definido nas decisões de projeto, uma requisição para a raiz `/` é associada ao arquivo `index.html`. Após a interpretação da mensagem, o servidor identifica o recurso solicitado, realiza sua leitura e constrói a resposta HTTP correspondente.

```text
HTTP/1.1 200 OK
Content-Length: 900
Content-Type: text/html
Connection: close

<!DOCTYPE html>
<html lang="pt-BR">
...
```

A resposta confirma que o arquivo `index.html` foi localizado corretamente e enviado ao navegador. Os campos `Content-Length` e `Content-Type` descrevem, respectivamente, o tamanho do corpo da resposta e o tipo do recurso retornado.

Além da requisição para a página principal, durante os testes foi observado que o navegador Firefox realizou automaticamente uma requisição para o recurso `favicon.ico`. Como essa requisição corresponde a um recurso distinto da página principal, ela também é tratada de forma independente pelo servidor, podendo ser processada em paralelo a outras conexões. A requisição observada foi:

```text
GET /favicon.ico HTTP/1.1
Host: 143.106.16.12:12000
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0
Accept: image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate
Connection: keep-alive
Referer: http://143.106.16.12:12000/
Priority: u=6
```

Assim como na requisição anterior, apenas a primeira linha é necessária para o processamento realizado pela aplicação. Nesse caso, o método identificado é `GET`, o recurso solicitado é `/favicon.ico` e a versão utilizada é `HTTP/1.1`. Como o arquivo está presente no diretório do servidor, ele é lido em modo binário e retornado ao cliente com uma resposta `200 OK` e o tipo MIME correspondente.