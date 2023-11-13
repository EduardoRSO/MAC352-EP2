from __future__ import annotations
import socket  # https://docs.python.org/3/library/socket.html
import os  # https://docs.python.org/3/library/os.html
from typing import List  # https://docs.python.org/3/library/typing.html
from threading import Thread, Lock  # https://docs.python.org/3/library/threading.html
from abc import ABC, abstractmethod
import sys
import socket
import select

# CONSTANTES

HOST = '127.0.0.1'
PORT = 6969
HEARTBEAT_TIMEOUT = 80085
SSL_TIMEOUT = 455
BUFFER_SIZE = 4096

HELLO = '0'
NOVO = '1'
SENHA = '2'
ENTRA = '3'
LIDERES='4'
LISTA_CONECTADOS = '5'
LISTA_TODOS = '6'
INICIA= '7'
DESAFIO = '8'
DESLOGA = '9'
MOVE = 'A'
ATRASO = 'B'
ENCERRA  ='C'
TCHAU = 'D'
TABULEIRO = 'E'
ACK = 'F'

class Logs:

    def __init__(self):
        self.lock = Lock()
        self.nome = 'logs.txt'
        try:
            self.logs = open(self.nome, 'r')
            print(f'    [+]Arquivo de logs encontrado')
            
        except:
            self.logs = open(self.nome,'a')
            print(f'    [-]Arquivo de logs não encontrado')
        self.logs.close()

    def logs_insere_nova_mensagem(self, mensagem: str):
        with self.lock:
            arquivo = open(self.nome, 'a')
            arquivo.write(mensagem)
            arquivo.close()



class Mensagens(ABC):

    #como verificar se a ultima execucao foi finalizada com sucesso? criar um arquivo 
    def mensagens_servidor_iniciado(self, tipo_servidor, host_servidor, porta_servidor):
        return f'Servidor {tipo_servidor} iniciado em {host_servidor}:{porta_servidor}\n'

    def mensagens_conexao_realizada(self, host_cliente, porta_cliente):
        return f'Conexao realizada com cliente em {host_cliente}:{porta_cliente}\n'

    def mensagens_login_sucesso(self, nome_usuario, host_cliente, porta_cliente):
        return f'Cliente {nome_usuario} em {host_cliente}:{porta_cliente} se conectou com sucesso\n'

    def mensagens_login_falha(self, nome_usuario, host_cliente, porta_cliente):
        return f'Cliente {nome_usuario} em {host_cliente}: {porta_cliente} falhou em se conectar\n'

    def mensagens_inicio_de_partida(self, nome_usuario, host_cliente, porta_cliente):
        return f'Cliente {nome_usuario} conectado em {host_cliente}:{porta_cliente} iniciou uma partida\n'

    def mensagens_fantasma_entrou(self, nome_usuario, host_cliente_1, porta_cliente_1, host_cliente_2, porta_cliente_2):
        return f'Cliente {nome_usuario} conectado em {host_cliente_2}:{porta_cliente_2} entrou na partida do cliente conectado em {host_cliente_1}:{porta_cliente_1}\n'

    def mensagens_fantasma_saiu(self, nome_usuario, host_cliente_1, porta_cliente_1, host_cliente_2, porta_cliente_2):
        return f'Cliente {nome_usuario} conectado em {host_cliente_2}:{porta_cliente_2} saiu da partida do cliente conectado em {host_cliente_1}:{porta_cliente_1}\n'


    def mensagens_finalizacao_partida(self, nome_usuario_1, host_cliente_1, porta_cliente_1, nome_usuario_2, host_cliente_2, porta_cliente_2, vencedor):
        if nome_usuario_2 == None:
            return f'Cliente {nome_usuario_1} conectado em {host_cliente_1}:{porta_cliente_1} finalizou a partida. O vencedor foi {vencedor}\n'
        else:
            return f'Cliente {nome_usuario_1} conectado em {host_cliente_1}:{porta_cliente_1} e Cliente {nome_usuario_2} conectado em {host_cliente_2}:{porta_cliente_2} finalizaram a partida. O vencedor foi {vencedor}\n'
         

    def mensagens_desconexao_inesperada_cliente(self, host_cliente, porta_cliente):
        return f'Cliente conectado em {host_cliente}:{porta_cliente} se desconectou inesperadamente\n'

    def mensagens_servidor_finalizado(self, tipo_servidor, host_servidor, porta_servidor):
        return f'Servidor {tipo_servidor} finalizado em {host_servidor}:{porta_servidor}\n'

#createlist?
class Usuarios:

    def __init__(self):
        self.lock = Lock()
        self.nome = 'usuarios.txt'
        usuarios = None
        try:
            usuarios = open(self.nome, 'r')
            print(f'    [+]Arquivo de usuários encontrado')
        except:
            usuarios = open(self.nome, 'a')
            print(f'    [-]Arquivo de usuários não encontrado')
        usuarios.close()

    def serializa(self):
        conteudo = []
        with self.lock:
            with open(self.nome, 'r') as arquivo:
                conteudo = arquivo.readlines()
        return conteudo


    def _formatacao_dos_dados(self, username, password, status, pontos, host, port):
        return f'{username} {password} {status} {pontos} {host} {port}\n'     
        
    def cria_novo_usuario(self, usuario, senha, host, porta) -> None:
        with self.lock:
            with open(self.nome, 'r') as arquivo:
                conteudo = arquivo.readlines()

            if usuario not in [linha.split()[0] for linha in conteudo]:
                with open(self.nome, 'a') as arquivo:
                    arquivo.write(self.formatacao_dos_dados(usuario, senha, 'offline', '0', host, port))
            

    def altera_senha_do_usuario(self, usuario, senha_antiga, senha_nova) -> None:
        with self.lock:
            with open(self.nome, 'r') as arquivo:
                conteudo = arquivo.readlines()
            for i in range(len(conteudo)):
                username, password, status, pontos, host, port = conteudo[i].split()
                if username == usuario:
                    password = senha_nova if password == senha_antiga else password
                    conteudo[i] = self.formatacao_dos_dados(username, password, status, pontos, host, port)
            with open(self.nome, 'w') as arquivo:
                arquivo.writelines(conteudo)          

    def atualiza_status(self, usuario, status_antigo, status_novo) -> None:
        with self.lock:
            with open(self.nome, 'r') as arquivo:
                conteudo = arquivo.readlines()
            for i in range(len(conteudo)):
                username, password, status, pontos, host, port = conteudo[i].split()
                if username == usuario:
                    status = status_novo if status == status_antigo else status
                    conteudo[i] = self.formatacao_dos_dados(username, password, status, pontos, host, port)
            with open(self.nome, 'w') as arquivo:
                arquivo.writelines(conteudo)           

    def lista_pontuacao(self) -> None:
        with self.lock:
            with open(self.nome, 'r') as arquivo:
                conteudo = arquivo.readlines()
            
            dados = []
            for linha in conteudo:    
                dados.append([linha.split()[0], linha.split()[3]])
            
            dados = sorted(dados, key = lambda x:x[1], reverse= True)
            for linha in dados:
                print(linha)

    def lista_nao_offline(self) -> None:
        with self.lock:
            with open(self.nome, 'r') as arquivo:
                conteudo = arquivo.readlines()
                for linha in conteudo:
                    if linha.split()[2] != 'offline':
                        print(linha, end='')

class Servidor(ABC):
    def __init__(self) -> None:
        self.interpretador = {
            HELLO: self.hello,
            NOVO: self.novo,
            SENHA: self.senha,
            ENTRA: self.entra,
            LIDERES: self.lideres,
            LISTA_CONECTADOS: self.conectados,
            LISTA_TODOS: self.todos,
            INICIA: self.inicia,
            DESAFIO: self.desafio,
            DESLOGA: self.desloga,
            ATRASO: self.atraso,
            ENCERRA: self.encerra,
            TCHAU: self.tchau,
            ACK: self.ack
        }

    def ack(self, dados: list):
        print(f' [+] Servidor().novo: Recebi {dados}')
        self._envia(dados[-1], ACK)

    def tchau(self, dados: list):
        print(f' [+] Servidor().novo: Recebi {dados}')
        self._envia(dados[-1], ACK)

    def encerra(self, dados: list):
        print(f' [+] Servidor().novo: Recebi {dados}')
        self._envia(dados[-1], ACK)

    def atraso(self, dados: list):
        print(f' [+] Servidor().novo: Recebi {dados}')
        self._envia(dados[-1], ACK)

    def desloga(self, dados: list):
        print(f' [+] Servidor().novo: Recebi {dados}')
        self._envia(dados[-1], ACK)

    def todos(self, dados: list):
        print(f' [+] Servidor().novo: Recebi {dados}')
        self._envia(dados[-1], ACK)

    def desafio(self, dados: list):
        print(f' [+] Servidor().novo: Recebi {dados}')
        self._envia(dados[-1], ACK)

    def inicia(self, dados: list):
        print(f' [+] Servidor().novo: Recebi {dados}')
        self._envia(dados[-1], ACK)

    def conectados(self, dados: list):
        print(f' [+] Servidor().novo: Recebi {dados}')
        self._envia(dados[-1], ACK)

    def lideres(self, dados: list):
        print(f' [+] Servidor().novo: Recebi {dados}')
        self._envia(dados[-1], ACK)

    def entra(self, dados: list):
        print(f' [+] Servidor().novo: Recebi {dados}')
        self._envia(dados[-1], ACK)

    def senha(self, dados: list):
        print(f' [+] Servidor().novo: Recebi {dados}')
        self._envia(dados[-1], ACK)

    def novo(self, dados: list):
        print(f' [+] Servidor().novo: Recebi {dados}')
        self._envia(dados[-1], ACK)

    def hello(self, dados: list):
        print(' [+] Servidor().hello: Recebi HELLO')
        self._envia(dados[-1],HELLO)
    
    def _envia(self, skt: socket, msg: str):
        host,port = skt.getpeername()
        skt.sendall(bytearray(msg.encode(encoding='utf-8')))


    def interpreta_pacote(self, dados:list):
        self.interpretador[dados[0][0]](dados)

class ServidorTCP(Servidor):
    def __init__(self, usuarios: Usuarios, logs: Logs, host:str, port:int):
        super().__init__()
        self.usuarios = usuarios
        self.logs = logs
        self.host = host
        self.port = port
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #?
        self.skt.bind((self.host,self.port))
        self.threads = []
        print(f' [+]Servidor TCP iniciado em {self.host}:{port}') 

    def cria_listener(self):
        self.skt.listen()
        while True:
            print(f' [+] ServidorTCP().cria_listener: esperando conexão')
            conn, addr = self.skt.accept()
            print(f' [+] ServidorTCP().cria_listener: conexão em {addr}')
            nova_thread = Thread(target=self.faz_leitura, args=(conn,addr))
            self.threads.append(nova_thread)
            nova_thread.start()

    def faz_leitura(self, conn, addr) -> None:
        with conn:
            print(f' [+] ServidorTCP().faz_leitura:  {addr}')
            while True:
                buffer = conn.recv(BUFFER_SIZE)
                print(f' [+] ServidorTCP().faz_leitura: Recebi {buffer}')
                if not buffer:
                    break
                self.interpreta_pacote([buffer.decode('utf-8'), conn])

    def faz_escrita(self, dados: List) -> None:
        buffer, conn = dados
        conn.sendall(buffer)            

class ServidorUDP(Servidor):
    def __init__(self, usuarios: Usuarios, logs: Logs, host:str, port:int):
        self.usuarios = usuarios
        self.logs = logs
        self.host = host
        self.port = port
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skt.bind(((self.host,self.port)))
        print(f'    [+]Servidor UDP iniciado em {self.host}:{port}') 

    def cria_listener(self):
            while True:
                self.faz_leitura()
    
    def faz_leitura(self) -> None:
        buffer, addr = self.skt.recvfrom(BUFFER_SIZE)
        print(f'    [+]Cliente UDP conectado em {addr}')
        self.interpreta_pacote([buffer, addr])    

    def faz_escrita(self, dados: List) -> None:
        buffer, addr = dados
        self.skt.sendto(buffer, addr)

    
class Auxiliares:

    def __init__(self):
        pass

    def auxiliares_envia_mensagem_para_socket(self, dados: List):
        pass

    def auxiliares_invoca_threads(self, servidor: Servidor) -> None:
        servidor.cria_listener()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = PORT

    u = Usuarios()
    l = Logs()

    servidorTCP = ServidorTCP(u, l, HOST, port)
    servidorUDP = ServidorUDP(u, l, HOST, port+1)

    servidores = []
    servidores.append(Thread(target = servidorTCP.cria_listener()))
    servidores.append(Thread(target = servidorUDP.cria_listener()))
    
    for tipo_de_servidor in servidores:
        tipo_de_servidor.start()


