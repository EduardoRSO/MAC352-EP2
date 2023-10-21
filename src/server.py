from __future__ import annotations
import socket  # https://docs.python.org/3/library/socket.html
import os  # https://docs.python.org/3/library/os.html
from typing import List  # https://docs.python.org/3/library/typing.html
from threading import Thread, Lock  # https://docs.python.org/3/library/threading.html
from abc import ABC, abstractmethod
import sys
# CONSTANTES

HOST = 'localhost'
PORT = 6969
HEARTBEAT_TIMEOUT = 80085
SSL_TIMEOUT = 455
BUFFER_SIZE = 4096


class Logs:

    def __init__(self):
        try:
            _logs = open('logs.txt', 'r')
            print(f'    [+]Arquivo de logs encontrado')
            
        except:
            _logs = open('logs.txt','a')
            print(f'    [-]Arquivo de logs não encontrado')
            
    def logs_insere_nova_mensagem(self, mensagem: Mensagens):
        pass


class Mensagens(ABC):

    def __init__(self):
        pass

    def mensagens_servidor_iniciado(self, dados: List) -> Mensagens:
        pass

    def mensagens_conexao_realizada(self, dados: List) -> Mensagens:
        pass

    def mensagens_login_sucesso(self, dados: List) -> Mensagens:
        pass

    def mensagens_login_falha(self, dados: List) -> Mensagens:
        pass

    def mensagens_inicio_de_partida(self, dados: List) -> Mensagens:
        pass

    def mensagens_fantasma_entrou(self, dados: List) -> Mensagens:
        pass

    def mensagens_fantasma_saiu(self, dados: List) -> Mensagens:
        pass

    def mensagens_finalizacao_partida(self, dados: List) -> Mensagens:
        pass

    def mensagens_desconexao_inesperada_cliente(self, dados: List) -> Mensagens:
        pass

    def mensagens_servidor_finalizado(self, dados: List) -> Mensagens:
        pass


class Usuarios:

    def __init__(self):
        try:
            _usuarios = open('usuarios.txt', 'r')
            print(f'    [+]Arquivo de usuários encontrado')
            
        except:
            _usuarios = open('usuarios.txt', 'a')
            print(f'    [-]Arquivo de usuários não encontrado')
             
    def usuarios_cria_novo_usuario(self, dados: List) -> None:
        pass

    def usuarios_altera_senha_do_usuario(self, dados: List) -> None:
        pass

    def usuarios_invade_partida(self, dados: List) -> None:
        pass

    def usuarios_atualiza_status(self, dados: List) -> None:
        pass

    def usuarios_retorna_Listagem(self, dados: List) -> None:
        pass


class Pontuacoes:
    def __init__(self):
        try:
            _pontuacoes = open('pontuacoes.txt', 'r')
            print(f'    [+]Arquivo de pontuações encontrado')
        except:
            _pontuacoes = open('pontuacoes.txt', 'a')
            print(f'    [-]Arquivo de pontuações não encontrado')
            
    def pontuacoes_adiciona_usuario(self, dados: List) -> None:
        pass

    def pontuacoes_atualiza_dados(self, dados: List) -> None:
        pass

    def pontuacoes_retorna_Listagem(self, dados: List) -> None:
        pass


class Servidores(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def servidores_faz_leitura(self, dados: List) -> None:
        pass

    @abstractmethod
    def servidores_faz_escrita(self, dados: List) -> None:
        pass

    @abstractmethod
    def servidores_interpreta_pacote(self, dados: List) -> None:
        pass

    @abstractmethod
    def servidores_cria_listener(self, dados: List) -> None:
        pass


class ServidoresTCP(Servidores):
    def __init__(self, usuarios: Usuarios, pontuacoes: Pontuacoes, logs: Logs):
        self.usuarios = usuarios
        self.pontuacoes = pontuacoes
        self.logs = logs
        self._skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self._skt.bind((HOST, PORT))
        print(f'    [+]Servidor TCP iniciado') 
        pass

    def servidores_cria_listener(self, dados: List):
        threads = []
        self._skt.listen()
        while True:
            conn, addr = self._skt.accept()
            nova_thread = Thread(target=self.servidores_faz_leitura, args=(conn,addr))
            threads.append(nova_thread)
            nova_thread.start()

    def servidores_faz_leitura(self, conn, addr) -> None:
        with conn:
            print(f'    [+]Cliente TCP conectado em {addr}')
            while True:
                buffer = conn.recv(BUFFER_SIZE)
                if not buffer:
                    break
                self.servidores_interpreta_pacote([buffer, conn])

    def servidores_interpreta_pacote(self, dados: List) -> None:
        buffer, conn = dados
        self.servidores_faz_escrita([buffer, conn])

    def servidores_faz_escrita(self, dados: List) -> None:
        buffer, conn = dados
        conn.sendall(buffer)            

class ServidoresUDP(Servidores):
    def __init__(self, usuarios: Usuarios, pontuacoes: Pontuacoes, logs: Logs):
        self.usuarios = usuarios
        self.pontuacoes = pontuacoes
        self.logs = logs
        self._skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._skt.bind((HOST, PORT))
        print(f'    [+]Servidor UDP iniciado') 

    def servidores_cria_listener(self):
            while True:
                self.servidores_faz_leitura()
    
    def servidores_faz_leitura(self) -> None:
        buffer, addr = self._skt.recvfrom(BUFFER_SIZE)
        print(f'    [+]Cliente UDP conectado em {addr}')
        self.servidores_interpreta_pacote([buffer, addr])    

    def servidores_interpreta_pacote(self, dados: list) -> None:
        buffer, addr = dados
        self.servidores_faz_escrita(buffer, addr)    

    def servidores_faz_escrita(self, dados: List) -> None:
        buffer, addr = dados
        self._skt.sendto(buffer, addr)

    
class Auxiliares:

    def __init__(self):
        pass

    #def auxiliares_envia_desafio(self, dados: List):
    #    pass

    def auxiliares_envia_mensagem_para_socket(self, dados: List):
        pass

    def auxiliares_invoca_threads(self, servidor: Servidores) -> None:
        servidor.servidores_cria_listener()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        port = (int)(sys.argv[1])
    else:
        port = PORT
    print(f'    [+]PORT = {port}')
    u = Usuarios()
    p = Pontuacoes()
    l = Logs()

    servidorTCP = ServidoresTCP(u, p, l)
    servidorUDP = ServidoresUDP(u, p, l)


