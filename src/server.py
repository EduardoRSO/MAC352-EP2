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


class Logs:

    def __init__(self):
        self._lock = Lock()
        self._nome = 'logs.txt'
        try:
            self._logs = open(self._nome, 'r')
            print(f'    [+]Arquivo de logs encontrado')
            
        except:
            self._logs = open(self._nome,'a')
            print(f'    [-]Arquivo de logs não encontrado')
        self._logs.close()

    def logs_insere_nova_mensagem(self, mensagem: str):
        with self._lock:
            arquivo = open(self._nome, 'a')
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


class Usuarios:

    def __init__(self):
        self._lock = Lock()
        self._nome = 'usuarios.txt'
        usuarios = None
        try:
            usuarios = open(self._nome, 'r')
            print(f'    [+]Arquivo de usuários encontrado')
        except:
            usuarios = open(self._nome, 'a')
            print(f'    [-]Arquivo de usuários não encontrado')
        usuarios.close()

    def _formatacao_dos_dados(self, username, password, status, pontos, host, port):
        return f'{username} {password} {status} {pontos} {host} {port}\n'     
        
    def usuarios_cria_novo_usuario(self, usuario, senha, host, porta) -> None:
        with self._lock:
            with open(self._nome, 'r') as arquivo:
                conteudo = arquivo.readlines()

            if usuario not in [linha.split()[0] for linha in conteudo]:
                with open(self._nome, 'a') as arquivo:
                    arquivo.write(self._formatacao_dos_dados(usuario, senha, 'offline', '0', host, port))
            

    def usuarios_altera_senha_do_usuario(self, usuario, senha_antiga, senha_nova) -> None:
        with self._lock:
            with open(self._nome, 'r') as arquivo:
                conteudo = arquivo.readlines()
            for i in range(len(conteudo)):
                username, password, status, pontos, host, port = conteudo[i].split()
                if username == usuario:
                    password = senha_nova if password == senha_antiga else password
                    conteudo[i] = self._formatacao_dos_dados(username, password, status, pontos, host, port)
            with open(self._nome, 'w') as arquivo:
                arquivo.writelines(conteudo)          

    def usuarios_atualiza_status(self, usuario, status_antigo, status_novo) -> None:
        with self._lock:
            with open(self._nome, 'r') as arquivo:
                conteudo = arquivo.readlines()
            for i in range(len(conteudo)):
                username, password, status, pontos, host, port = conteudo[i].split()
                if username == usuario:
                    status = status_novo if status == status_antigo else status
                    conteudo[i] = self._formatacao_dos_dados(username, password, status, pontos, host, port)
            with open(self._nome, 'w') as arquivo:
                arquivo.writelines(conteudo)           

    def usuarios_lista_pontuacao(self) -> None:
        with self._lock:
            with open(self._nome, 'r') as arquivo:
                conteudo = arquivo.readlines()
            
            dados = []
            for linha in conteudo:    
                dados.append([linha.split()[0], linha.split()[3]])
            
            dados = sorted(dados, key = lambda x:x[1], reverse= True)
            for linha in dados:
                print(linha)

    def usuarios_lista_nao_offline(self) -> None:
        with self._lock:
            with open(self._nome, 'r') as arquivo:
                conteudo = arquivo.readlines()
                for linha in conteudo:
                    if linha.split()[2] != 'offline':
                        print(linha, end='')

class Servidor(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def servidor_faz_leitura(self, dados: List) -> None:
        pass

    @abstractmethod
    def servidor_faz_escrita(self, dados: List) -> None:
        pass

    @abstractmethod
    def servidor_interpreta_pacote(self, dados: List) -> None:
        pass

    @abstractmethod
    def servidor_cria_listener(self, dados: List) -> None:
        pass


class ServidorTCP(Servidor):
    def __init__(self, usuarios: Usuarios, logs: Logs, port):
        self.usuarios = usuarios
        self.logs = logs
        self._skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self._skt.bind((HOST, PORT))
        self._threads = []
        print(f'    [+]Servidor TCP iniciado em {HOST}:{port}') 
        pass

    def servidor_cria_listener(self, dados: List):
        self._skt.listen()
        while True:
            conn, addr = self._skt.accept()
            nova_thread = Thread(target=self.servidor_faz_leitura, args=(conn,addr))
            self._threads.append(nova_thread)
            nova_thread.start()

    def servidor_faz_leitura(self, conn, addr) -> None:
        with conn:
            print(f'    [+]Cliente TCP conectado em {addr}')
            while True:
                buffer = conn.recv(BUFFER_SIZE)
                if not buffer:
                    break
                self.servidor_interpreta_pacote([buffer, conn])

    def servidor_interpreta_pacote(self, dados: List) -> None:
        buffer, conn = dados
        self.servidor_faz_escrita([buffer, conn])

    def servidor_faz_escrita(self, dados: List) -> None:
        buffer, conn = dados
        conn.sendall(buffer)            

class ServidorUDP(Servidor):
    def __init__(self, usuarios: Usuarios,logs: Logs, port):
        self.usuarios = usuarios
        self.logs = logs
        self._skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._skt.bind((HOST, PORT))
        print(f'    [+]Servidor UDP iniciado em {HOST}:{port}') 

    def servidor_cria_listener(self):
            while True:
                self.servidor_faz_leitura()
    
    def servidor_faz_leitura(self) -> None:
        buffer, addr = self._skt.recvfrom(BUFFER_SIZE)
        print(f'    [+]Cliente UDP conectado em {addr}')
        self.servidor_interpreta_pacote([buffer, addr])    

    def servidor_interpreta_pacote(self, dados: list) -> None:
        buffer, addr = dados
        self.servidor_faz_escrita(buffer, addr)    

    def servidor_faz_escrita(self, dados: List) -> None:
        buffer, addr = dados
        self._skt.sendto(buffer, addr)

    
class Auxiliares:

    def __init__(self):
        pass

    #def auxiliares_envia_desafio(self, dados: List):
    #    pass

    def auxiliares_envia_mensagem_para_socket(self, dados: List):
        pass

    def auxiliares_invoca_threads(self, servidor: Servidor) -> None:
        servidor.servidor_cria_listener()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        port = (int)(sys.argv[1])
    else:
        port = PORT

    u = Usuarios()
    l = Logs()

    u.usuarios_lista_nao_offline()
    u.usuarios_cria_novo_usuario('user1', 'senha1', 'host1', 'port1') 
    u.usuarios_cria_novo_usuario('user2', 'senha2', 'host2', 'port2')   
    u.usuarios_atualiza_status('user1', 'offline', 'online')
    u.usuarios_altera_senha_do_usuario('user1', 'senha1', 'passw1')
    u.usuarios_atualiza_status('user2', 'offline', 'jogando')
    u.usuarios_lista_pontuacao()   
    #servidorTCP = ServidorTCP(u, p, l, port)
    #servidorUDP = ServidorUDP(u, p, l, port)


