# importando a biblioteca para uso de classe de dados
from dataclasses import dataclass

# importando biblioteca de socket
import socket
 
# importando multithreading
from _thread import *
import threading
 
# classe para armazenar os dados da request http
@dataclass
class HTTPRequest:
  method: str
  route: str
  protocol: str

# leitor de arquivo, também trata exceção de arquivo não encontrado
def file_parser(file_path):
    print("[FILE] Parsing file from: " + file_path)
    try:
        with open(file_path, "rb") as file:
            content = file.read()
            return content

    except FileNotFoundError as FnF:
        print("[ERROR] Could not find file: " + file_path)
        raise FnF

# criação da resposta para a request http, também trata exceção de método de request não suportado
def create_response():
    if(HTTPRequest.method == 'GET'):
        try:
            html_content = file_parser(HTTPRequest.route[1:])
            # criação da resposta HTTP apropriada
            status_line = b"HTTP/1.1 200 OK\r\n\r\n"
            response = status_line + html_content

        except FileNotFoundError:
            # caso não encontre o arquivo, retorna uma resposta 404
            status_line = b"HTTP/1.1 404 Not Found\r\n\r\n"
            not_found_content = file_parser('Errors/NotFound.html')
            response = status_line + not_found_content
    
    else:
            # caso o método não seja suportado (HEAD, POST, PUT, DELETE, TRACE, OPTIONS e CONNECT) retorna uma resposta 405
            status_line = b"HTTP/1.1 405 Not Supported\r\n\r\n"
            not_supported_method = file_parser('Errors/NotSupportedMethod.html')
            response = status_line + not_supported_method

    return response

# lida com as requisições do cliente
def handle_client(conn, addr):
    print(f"[CONNECTION] IP: {addr[0]}, Port: {addr[1]} connected.")
    
    # recebe a request, decodifica de byte para string, e divide em linhas
    msg_http = conn.recv(1024)
    msg_str = msg_http.decode('utf-8')
    linhas = msg_str.split('\r\n')
    
    # captura os 3 primeiros atributos da primeira linha, método, rota (caminho do arquivo desejado) e protocolo
    HTTPRequest.method, HTTPRequest.route, HTTPRequest.protocol = linhas[0].split(' ')
    print(f"[REQUEST] Method: {HTTPRequest.method}.  Route: {HTTPRequest.route}.  Protocol: {HTTPRequest.protocol}.")
    
    # envia a resposta para o cliente e fecha a conexão
    conn.send(create_response())               
    conn.close()
    print(f"[CONNECTION] IP: {addr[0]}, Port: {addr[1]} disconnected.")
 
def main():
    # porta, ip do servidor e endereço
    SERVER = '127.0.0.1'
    PORT = 12345
    ADDR = (SERVER, PORT)

    # iniciando e bindando o socket no endereço
    connectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connectionSocket.bind(ADDR)
    connectionSocket.listen(5)
    print("Server is listening.")
 
    while True:
        # estabelece a conexão com o cliente
        conn, addr = connectionSocket.accept()
        # inicia uma nova thread
        response_thread = threading.Thread(target = handle_client, name = f'Connection thread', args = (conn, addr))
        response_thread.start()
 
if __name__ == '__main__':
    main()