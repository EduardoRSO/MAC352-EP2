from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
import sys
import socket
import select
import time
from pacman import *

HOST = '127.0.0.1'
PORT = '8989'
BUFFER_SIZE = 4096
PROMPT = "Pac-Man> "

# Identificador dos comandos nos pacotes
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

# Identificador dos comandos recebidos via input

C_NOVO = 'novo'
C_SENHA = 'senha'
C_ENTRA = 'entra'
C_LIDERES = 'lideres'
C_LISTA = 'l'
C_INICIA ='inicia'
C_DESAFIO = 'desafio'
C_MOVE = 'move'    
C_ATRASO = 'atraso'
C_ENCERRA = 'encerra'
C_SAI = 'sai'
C_TCHAU ='tchau'

class Comandos():

    def constroi_pacote(self, tipo, argumentos: list):
        string = tipo
        for item in argumentos:
            string+= str(len(item))+item
        return string

    def __init__(self, cliente: Cliente) -> None:
        self.c = cliente
    
    def novo(self, argumentos: list) -> None:
        self.envia_mensagem(self.c.serv_skt,self.constroi_pacote(NOVO, argumentos))
        resultado, msg = self.recebe_mensagem(self.c.serv_skt)

    def senha(self, dados: list) -> None:
        self.envia_mensagem(self.c.serv_skt,self.constroi_pacote(SENHA,dados))
        resultado, msg = self.recebe_mensagem(self.c.serv_skt)
    
    def entra(self, dados: list) -> None:
        self.envia_mensagem(self.c.serv_skt,self.constroi_pacote(ENTRA,dados))
        resultado, msg = self.recebe_mensagem(self.c.serv_skt)
        if resultado == True:
            self.c.estado = 'CONECTADO'

    def lideres(self, dados: list) -> None:
        self.envia_mensagem(self.c.serv_skt,self.constroi_pacote(LIDERES,dados))
        resultado, msg = self.recebe_mensagem(self.c.serv_skt)
    
    def l(self,dados: list) -> None:
        self.envia_mensagem(self.c.serv_skt,self.constroi_pacote(LISTA_CONECTADOS,dados))
        resultado, msg = self.recebe_mensagem(self.c.serv_skt)

    
    def inicia(self,dados: list) -> None:
        self.envia_mensagem(self.c.serv_skt,self.constroi_pacote(INICIA,dados))
        resultado, msg = self.recebe_mensagem(self.c.serv_skt)
        if resultado == True:
            self.c.estado = 'JOGANDO'
    
    def desafio(self, dados: list) -> None:
        self.envia_mensagem(self.c.serv_skt,self.constroi_pacote(DESAFIO,dados))
        resultado, msg = self.recebe_mensagem(self.c.serv_skt)
        if resultado == True:
            self.c.estado = 'JOGANDO'
    
    def move(self, dados: list) -> None:
        self.envia_mensagem(self.c.serv_skt,self.constroi_pacote(MOVE,dados))
        resultado, msg = self.recebe_mensagem(self.c.serv_skt)

    
    def atraso(self, dados: list) -> None:
        self.envia_mensagem(self.c.serv_skt,self.constroi_pacote(ATRASO,dados))
        resultado, msg = self.recebe_mensagem(self.c.serv_skt)

    
    def encerra(self, dados: list) -> None:
        self.envia_mensagem(self.c.serv_skt,self.constroi_pacote(ENCERRA,dados))
        resultado, msg = self.recebe_mensagem(self.c.serv_skt)
        if resultado == True:
            self.c.estado = 'CONECTADO'
    
    def sai(self, dados: list) -> None:
        self.envia_mensagem(self.c.serv_skt,self.constroi_pacote(SAI,dados))
        resultado, msg = self.recebe_mensagem(self.c.serv_skt)
        if resultado == True:
            self.c.estado = 'NEUTRO'
    
    def tchau(self, dados: list) -> None:
        self.envia_mensagem(self.c.serv_skt,self.constroi_pacote(TCHAU,dados))
        resultado, msg = self.recebe_mensagem(self.c.serv_skt)
        exit()

    def envia_tabuleiro(self, dados: list):  
        return json.dumps(self.pacman.tabuleiro)
        
    def recebe_tabuleiro(self, tabuleiro_str):
        self.pacman = Pacman(json.loads(tabuleiro_str))

    def envia_desafio(self, dados: list):
        usuario, host, port = dados
        oponente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        oponente.connect((host, port))
        self.envia_mensagem(dados, self.estado.desafio(dados))

    def processa_resultado_do_jogo():
        pass

    def envia_mensagem(self, skt: socket, mensagem: str):
        print(f' [+] Comandos().envia_mensagem: Enviei {mensagem}')
        skt.sendall(bytearray(mensagem.encode(encoding='utf-8')))

    def recebe_mensagem(self, skt: socket):
        msg = skt.recv(BUFFER_SIZE).decode('utf-8')
        if msg == ACK:
            print(f' [+] Comandos().recebe_mensagem: Recebi ACK')
            return True, msg
        else:
            print(f' [-] Comandos().recebe_mensagem: Não recebi ACK')
            return False, msg

class Cliente():
    oponente = None

    def __init__(self) -> None:
        self.comandos = Comandos(self)
        self.estado = 'NEUTRO'
        self.usuario = 'u'
        self.senha = 's'
        self.pontuacao = 0
        self.latencia = []
        self.heartbeat = [] 
        self.pacman = Pacman(ESTADO_INICIAL)

        self.interpretador = {
            C_NOVO: self.comandos.novo,
            C_SENHA: self.comandos.senha,
            C_ENTRA: self.comandos.entra,
            C_LIDERES: self.comandos.lideres,
            C_LISTA:  self.comandos.l,
            C_INICIA: self.comandos.inicia,
            C_DESAFIO: self.comandos.desafio,
            C_MOVE: self.comandos.move,
            C_ATRASO: self.comandos.atraso,
            C_ENCERRA: self.comandos.encerra,
            C_SAI: self.comandos.sai,
            C_TCHAU: self.comandos.tchau
        }
        self.comandos_do_estado = {
            'NEUTRO': [C_NOVO, C_ENTRA, C_TCHAU],
            'CONECTADO': [C_SENHA, C_LIDERES, C_LISTA, C_INICIA, C_DESAFIO, C_SAI],
            'JOGANDO': [C_MOVE, C_ATRASO, C_ENCERRA]
        }

    def processa_oponente():
        pass

    def processa_cliente(self):
        while True:
            comando = input(PROMPT)
            if comando != '':
                acao = comando.split()[0]
                argumentos = comando.split()[1:]
                if acao in self.comandos_do_estado[self.estado]:
                    print(f' [+] Cliente().processa_cliente: Recebi o comando {acao} com argumentos {argumentos}')
                    self.interpretador[acao](argumentos)


class ClienteTCP(Cliente):
    _estado = None
    def __init__(self, host, port) -> None:
        super().__init__()
        self.host = host
        self.port = int(port)
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #?
        self.skt.bind((self.host,self.port))
        print(self.host, self.port, self.usuario, self.senha, self.latencia, self.heartbeat)
        print(f' [+] ClienteTCP().__init__: {host}:{port}')

    def conecta_com_servidor(self, serv_host, serv_port):
        self.serv_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_skt.connect((serv_host, int(serv_port)))
        self.serv_skt.sendall(bytearray(HELLO.encode(encoding='utf-8')))
        msg = self.serv_skt.recv(BUFFER_SIZE).decode('utf-8')
        if msg == HELLO:
            print(f' [+] ClienteTCP().conecta_com_servidor: Recebi HELLO')
            self.processa_cliente()
        else:
            print(f' [-] ClienteTCP().conecta_com_servidor: Não recebi HELLO')

class ClienteUDP(Cliente):
    pass
        

if __name__ == '__main__':
    try:
        dummy, host, port, tipo = sys.argv
    except:
        dummy, host, port, tipo = ['dummy',HOST,PORT,'TCP']
    c = ''
    if tipo == 'TCP':
        c = ClienteTCP(host, port)
    elif tipo == 'UDP':
        c = ClienteUDP(host, port)
    else:
        c = ClienteTCP(host, port)
    c.conecta_com_servidor(HOST, 6969)

    