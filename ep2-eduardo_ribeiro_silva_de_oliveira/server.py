from __future__ import annotations
import socket  # https://docs.python.org/3/library/socket.html
import os  # https://docs.python.org/3/library/os.html
from typing import List  # https://docs.python.org/3/library/typing.html
from threading import Thread, Lock  # https://docs.python.org/3/library/threading.html
from abc import ABC, abstractmethod
import sys
import socket
import select
import time
import random

# CONSTANTES

HOST = '127.0.0.1'
PORT = 6969
TIMEOUT = 20
SSL_TIMEOUT = 455
BUFFER_SIZE = 4096
OFFLINE = 'offline'
ONLINE = 'online'
JOGANDO = 'jogando'
PONTOS = '0'

HELLO = '0'
NOVO = '1'
SENHA = '2'
ENTRA = '3'
LIDERES='4'
LISTA_CONECTADOS = '5'
LISTA_TODOS = '6'
INICIA= '7'
DESAFIO = '8'
SAI = '9'
MOVE = 'A'
ATRASO = 'B'
ENCERRA  ='C'
TCHAU = 'D'
TABULEIRO = 'E'
ACK = 'F'
HEARTBEAT = 'G'
NACK = 'H'
END='|'


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

    def insere_nova_mensagem(self, mensagem: str):
        with self.lock:
            arquivo = open(self.nome, 'a')
            arquivo.write(mensagem)
            arquivo.close()



class Mensagens(ABC):

    #como verificar se a ultima execucao foi finalizada com sucesso? criar um arquivo 
    def servidor_iniciado(tipo_servidor, host_servidor, porta_servidor):
        return f'Servidor {tipo_servidor} iniciado em {host_servidor}:{porta_servidor}\n'

    def usuario_desconectado(dados):
        return f'Usuario {dados[0]} desconectou\n'
    
    def partida_encerrada(dados):
        return f'Usuário {dados[0]} encerrou a partida\n'
    
    def atraso_solicitado(dados):
        return f'Usuário {dados[0]} solicitou atraso de {dados[1]}\n'

    def usuario_saiu(dados):
        return f'Usuário {dados[0]} saiu\n'
    
    def desafio_solicitado(dados):
        return f'Usuário {dados[0]} foi desafiado\n'

    def lista_solicitada(dados):
        return f'usuaŕio {dados[0]} solicitou a lista\n'

    def lideres_solicitada(dados):
        return f'usuaŕio {dados[0]} solicitou lideres\n'

    def conexao_realizada(dados):
        return f'Conexao realizada com cliente em {dados[1]}\n'

    def login_sucesso(dados):
        return f'Cliente {dados[0]} em {dados[1]} se conectou com sucesso\n'

    def login_falha(dados):
        return f'Cliente {dados[0]} em {dados[1]} falhou em se conectar\n'

    def inicio_de_partida(dados):
        return f'Usuário {dados[0]} iniciou uma partida\n'
    
    def senha_solicitada(dados):
        return f'Usuário {dados[0]} solicitou a troca da senha\n'
    
    def novo_solicitado(dados):
        return f'Usuário {dados[0]} criado\n'

    def desconexao_inesperada_cliente(host_cliente, porta_cliente):
        return f'Cliente conectado em {host_cliente}:{porta_cliente} se desconectou inesperadamente\n'

    def servidor_finalizado(tipo_servidor, host_servidor, porta_servidor):
        return f'Servidor {tipo_servidor} finalizado em {host_servidor}:{porta_servidor}\n'

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
                conteudo = [linha.split(' ') for linha in arquivo.readlines()]
        return conteudo


    def _formatacao_dos_dados(self, username, password, status, pontos, host, port):
        return f'{username} {password} {status} {pontos} {host} {port}\n'     
        
    def cria_novo_usuario(self, dados: list, skt: socket) -> None:
        usuario = dados[0]
        senha = dados[1]
        try:
            host,port = skt.getpeername()
        except:
            host,port = self.userAddress
        with self.lock:
            conteudo = []
            
            with open(self.nome, 'r') as arquivo:
                conteudo = arquivo.readlines()
            
            if usuario not in [linha.split()[0] for linha in conteudo]:
                with open(self.nome, 'a') as arquivo:
                    arquivo.write(self._formatacao_dos_dados(usuario, senha, OFFLINE, PONTOS, host, port))
                    return True
            return False


    def altera_senha_do_usuario(self, dados: list, skt: socket) -> None:
        usuario = dados[0]
        senha_antiga = dados[1]
        senha_nova = dados[2]
        try:
            host_novo,port_novo = skt.getpeername()
        except:
            host_novo,port_novo = self.userAddress    
        with self.lock:
            conteudo = []
            
            with open(self.nome, 'r') as arquivo:
                conteudo = arquivo.readlines()
            
            for i in range(len(conteudo)):
                username, password, status, pontos, host, port = conteudo[i].split()
                if username == usuario:
                    password = senha_nova if password == senha_antiga else password
                    conteudo[i] = self._formatacao_dos_dados(username, password, status, pontos, host_novo, port_novo)
                    with open(self.nome, 'w') as arquivo:
                        arquivo.writelines(conteudo)          
                    return True
            return False

    def atualiza_status(self, dados: list, skt: socket) -> None:
        usuario = dados[0]
        status_antigo = dados[1]
        status_novo = dados[2]
        try:
            host_novo,port_novo = skt.getpeername()
        except:
            host_novo,port_novo = self.userAddress
            
        with self.lock:
            conteudo = []
            
            with open(self.nome, 'r') as arquivo:
                conteudo = arquivo.readlines()
            
            for i in range(len(conteudo)):
                username, password, status, pontos, host, port = conteudo[i].split()
                if username == usuario:
                    status = status_novo if status == status_antigo else status
                    conteudo[i] = self._formatacao_dos_dados(username, password, status, pontos, host_novo, port_novo)
                    with open(self.nome, 'w') as arquivo:
                        arquivo.writelines(conteudo)
                    return True
            return False           

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
            conectados = ''
            with open(self.nome, 'r') as arquivo:
                conteudo = arquivo.readlines()
                for linha in conteudo:
                    if linha.split()[2] != 'offline':
                        conectados += linha
            return conectados

class Servidor(ABC):
    def __init__(self, usuarios: Usuarios, logs: Logs, host:str, port:int) -> None:
            self.usuarios = usuarios
            self.logs = logs
            self.host = host
            self.port = port
            self.interpretador = {
            HELLO: self.hello,
            NOVO: self.novo,
            SENHA: self.senha,
            ENTRA: self.entra,
            LIDERES: self.lideres,
            LISTA_CONECTADOS: self.conectados,
            INICIA: self.inicia,
            DESAFIO: self.desafio,
            SAI: self.sai,
            ATRASO: self.atraso,
            ENCERRA: self.encerra,
            TCHAU: self.tchau,
        }

    def _extrai_dados(self, pacote:str):
        dados = []
        inicio = 2
        if len(pacote) == 1:
            return pacote
        tamanho = int(pacote[1])
        while inicio < len(pacote):
            if tamanho != '0':
                dados.append(pacote[inicio:inicio+tamanho])
            inicio = inicio+tamanho+1
            tamanho = int(pacote[inicio-1]) if len(pacote) > inicio-1 else None
        return dados

    def tchau(self, dados: list):
        self.logs.insere_nova_mensagem(Mensagens.usuario_desconectado(dados))
        self.envia(dados[-1], ACK)

    def encerra(self, dados: list):
        self.logs.insere_nova_mensagem(Mensagens.partida_encerrada(dados))
        if True == self.usuarios.atualiza_status([self._extrai_dados(dados[0])[0], JOGANDO, ONLINE], dados[-1]):
            self.envia(dados[-1], ACK)
        else:
            self.envia(dados[-1], NACK)

    def atraso(self, dados: list):
        self.logs.insere_nova_mensagem(Mensagens.atraso_solicitado(dados))
        self.envia(dados[-1], ACK)

    def sai(self, dados: list):
        self.logs.insere_nova_mensagem(Mensagens.usuario_saiu(dados))
        if True == self.usuarios.atualiza_status([self._extrai_dados(dados[0])[0], ONLINE, OFFLINE], dados[-1]):
            self.envia(dados[-1], ACK)
        else:
            self.envia(dados[-1], NACK)

    def desafio(self, dados: list):
        self.logs.insere_nova_mensagem(Mensagens.desafio_solicitado([dados]))
        usuario = self._extrai_dados(dados[0])[0]
        conectados = self.usuarios.serializa()
        msg = ACK
        for conectado in conectados:
            print(conectado[0] , usuario)
            if conectado[0] == usuario:
                host = conectado[4]
                port = conectado[5]
                msg = f'{host} {port}'
        self.envia(dados[-1], msg)
        

    def inicia(self, dados: list):
        self.logs.insere_nova_mensagem(Mensagens.inicio_de_partida(dados))
        if True == self.usuarios.atualiza_status([self._extrai_dados(dados[0])[0], ONLINE, JOGANDO], dados[-1]):
            self.envia(dados[-1], ACK)
        else:
            self.envia(dados[-1], NACK)

    def conectados(self, dados: list):
        self.logs.insere_nova_mensagem(Mensagens.lista_solicitada(dados))
        conectados = self.usuarios.lista_nao_offline()
        self.envia(dados[-1], conectados)

    def lideres(self, dados: list):
        self.logs.insere_nova_mensagem(Mensagens.lideres_solicitaa(dados))
        self.usuarios.lista_pontuacao()
        self.envia(dados[-1], ACK)

    def entra(self, dados: list):
        if True == self.usuarios.atualiza_status([self._extrai_dados(dados[0])[0], OFFLINE, ONLINE], dados[-1]):
            self.envia(dados[-1], ACK)
            self.logs.insere_nova_mensagem(Mensagens.login_sucesso(dados))
        else:
            self.envia(dados[-1], NACK)
            self.logs.insere_nova_mensagem(Mensagens.login_falha(dados))

    def senha(self, dados: list):
        self.logs.insere_nova_mensagem(Mensagens.senha_solicitada(dados))
        if True == self.usuarios.altera_senha_do_usuario(self._extrai_dados(dados[0]), dados[-1]):
            self.envia(dados[-1], ACK)
        else:
            self.envia(dados[-1], NACK)

    def novo(self, dados: list):
        self.logs.insere_nova_mensagem(Mensagens.novo_solicitado(dados))
        if True == self.usuarios.cria_novo_usuario(self._extrai_dados(dados[0]), dados[-1]):
            self.envia(dados[-1], ACK)
        else:
            self.envia(dados[-1], NACK)

    def hello(self, dados: list):
        self.logs.insere_nova_mensagem(Mensagens.conexao_realizada(dados))
        self.envia(dados[-1],HELLO)

    def recebe_mensagem(self, skt: socket):
        msg = skt.recv(BUFFER_SIZE).decode('utf-8')
        if msg == ACK:
            return True, msg
        else:
            return False, msg

    def envia(self, skt: socket, msg: str):
        skt.sendall(bytearray(msg.encode(encoding='utf-8')))

    def interpreta_pacote(self, dados:list):
        self.interpretador[dados[0][0]](dados)

class ServidorTCP(Servidor):
    def __init__(self, usuarios: Usuarios, logs: Logs, host:str, port:int):
        super().__init__(usuarios, logs, host, port)
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #?
        self.skt.bind((self.host,self.port))
        self.host, self.port = self.skt.getsockname()
        self.threads = []
        self.logs.insere_nova_mensagem(Mensagens.servidor_iniciado('TCP', host, port))

    def cria_listener(self):
        self.skt.listen()
        while True:
            conn, addr = self.skt.accept()
            nova_thread = Thread(target=self.faz_leitura, args=(conn,addr))
            self.threads.append(nova_thread)
            nova_thread.start()

    def faz_leitura(self, conn, addr) -> None:

            while True:
                buffer = conn.recv(BUFFER_SIZE)
                if not buffer:
                    break
                self.interpreta_pacote([buffer.decode('utf-8'), conn])

class ServidorUDP(Servidor):
    def __init__(self, usuarios: Usuarios, logs: Logs, host:str, port:int):
        super().__init__(usuarios, logs, host, port)
        self.usuarios = usuarios
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skt.bind(((self.host,self.port)))
        self.logs.insere_nova_mensagem(Mensagens.servidor_iniciado('UDP', host,port))

    def cria_listener(self):
            while True:
                self.faz_leitura()
    
    def faz_leitura(self) -> None:
        buffer, addr = self.skt.recvfrom(BUFFER_SIZE)
        self.userAddress = (addr[0], addr[1])
        self.usuarios.userAddress = self.userAddress
        self.interpreta_pacote([buffer.decode('utf-8'), self.skt])    

    def envia(self, skt: socket, msg: str):
        skt.sendto(bytearray(msg.encode(encoding='utf-8')),self.userAddress)
    
class Auxiliares:

    def __init__(self):
        pass

    def auxiliaresenvia_mensagem_para_socket(self, dados: List):
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


