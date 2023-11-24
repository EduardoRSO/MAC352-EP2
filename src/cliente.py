from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
import sys
import socket
import time
from pacman import *
from threading import Thread, Lock  # https://docs.python.org/3/library/threading.html

HOST = '127.0.0.1'
PORT = '8989'
BUFFER_SIZE = 4096
PROMPT = "Pac-Man> "
CONSTANTE = 2
JOGANDO = 'jogando'
CONECTADO = 'online'
NEUTRO = 'offline'
DESAFIANDO = 'desafiando'

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
HEARTBEAT = 'G'
NACK ='H'
END='|'

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
C_HEARTBEAT = HEARTBEAT


comandos_validos = [C_NOVO, C_SENHA, C_ENTRA, C_LIDERES, C_LISTA, C_INICIA, C_DESAFIO, C_MOVE, C_ATRASO, C_ENCERRA, C_SAI, C_TCHAU]

class Comandos():

    def constroi_pacote(self, tipo, argumentos: list):
        string = tipo
        for item in argumentos:
            string+= str(len(item))+item
        return string

    def __init__(self, cliente: Cliente) -> None:
        self.c = cliente
    
    def novo(self, argumentos: list) -> None:
        print(f' Comandos().novo: Enviei {argumentos}')
        self.envia_mensagem(self.c.skt,self.constroi_pacote(NOVO, argumentos))
        resultado, msg = self.recebe_mensagem(self.c.skt)

    def senha(self, dados: list) -> None:
        print(f' Comandos().senha: Enviei {dados}')
        self.envia_mensagem(self.c.skt,self.constroi_pacote(SENHA, [self.c.usuario]+dados))
        resultado, msg = self.recebe_mensagem(self.c.skt)
    
    def entra(self, dados: list) -> None:
        print(f' Comandos().entra: Enviei {dados}')
        self.envia_mensagem(self.c.skt,self.constroi_pacote(ENTRA,dados))
        resultado, msg = self.recebe_mensagem(self.c.skt)
        if resultado == True:
            self.c.usuario = dados[0]
            self.c.senha = dados[1]
            self.c.estado = CONECTADO

    def lideres(self, dados: list) -> None:
        print(f' Comandos().lideres: Enviei {dados}')
        self.envia_mensagem(self.c.skt,self.constroi_pacote(LIDERES,dados))
        resultado, msg = self.recebe_mensagem(self.c.skt)
    
    def l(self,dados: list) -> None:
        print(f' Comandos().l: Enviei {dados}')
        self.envia_mensagem(self.c.skt,self.constroi_pacote(LISTA_CONECTADOS,dados))
        resultado, msg = self.recebe_mensagem(self.c.skt)
        if resultado == False:
            print(f'{PROMPT} CONECTADOS:')
            for index, linha in enumerate(msg.split('\n')[:-1]):
                print(f'       >[{index}]: {linha}')
    
    def inicia(self,dados: list) -> None:
        print(f' Comandos().inicia: Enviei {dados}')
        self.envia_mensagem(self.c.skt,self.constroi_pacote(INICIA,[self.c.usuario]))
        resultado, msg = self.recebe_mensagem(self.c.skt)
        if resultado == True:
            self.c.estado = JOGANDO
            self.c.pacman.mostra_tabuleiro()
            
    
    def desafio(self, dados: list) -> None:
        print(f' [+] Comandos().desafio: Enviei {dados}')
        self.envia_mensagem(self.c.skt,self.constroi_pacote(DESAFIO,dados))
        resultado, msg = self.recebe_mensagem(self.c.skt)
        if not resultado:
            #self.oponente_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host,port = msg.split()
            port = int(port)+CONSTANTE
            print(f' [+] Comandos().desafio: Conectando em {host}:{port}')    
            self.c.desafio_atuante = socket.socket()
            self.c.desafio_atuante.connect((host,port))
            #self.c.desafio_atuante.sendall(bytearray(HELLO.encode(encoding='utf-8')))
            self.c.desafio_ouvinte.close()
            self.c.estado = DESAFIANDO
            #self.c.interpretador[C_MOVE] = self.move_remoto
            self.recebe_tabuleiro(self.c.desafio_atuante)
            self.processa_desafio()
            
    
    def processa_desafio(self):
        msg = ''
        while msg != 'encerra':
            anterior = self.c.pacman._tabuleiro 
            while anterior == self.c.pacman._tabuleiro:
                self.recebe_tabuleiro(self.c.desafio_atuante)
            self.c.pacman.mostra_tabuleiro()
            msg = input(f'{PROMPT}').split(' ')
            if msg == ['encerra']:
                self.move_remoto([NACK])
                self.c.desafio_atuante.close()
                self.c.desafio_atuante = None
                break
            else:
                self.move_remoto(msg)
        self.c.processa_cliente()
            

    def move(self, dados: list) -> None:
        self.c.pacman.mostra_tabuleiro()
        self.c.pacman.movimenta_fantasmas_locais()
        self.c.pacman.colisao_fantasma_local()
        time.sleep(1)
        self.c.pacman.mostra_tabuleiro()
        if self.c.desafio_atuante != None:
            self.envia_tabuleiro(self.c.desafio_atuante)
            #print(f'esperando {self.c.desafio_atuante}')
            resultado, direcao = self.recebe_mensagem(self.c.desafio_atuante)
            #print(f'recebi {direcao}')
            if direcao != NACK:
                self.c.pacman.movimenta_fantasma_remoto(direcao)
                self.c.pacman.colisao_fantasma_remoto()
            else:
                self.c.desafio_atuante.close()
                self.c.desafio_atuante = None
            time.sleep(1)
            self.c.pacman.mostra_tabuleiro()
        self.c.pacman.movimenta_pacman(dados[0])
        self.c.pacman.colisao_pacman()
        time.sleep(1)
        self.c.pacman.mostra_tabuleiro()
    
    def move_remoto(self, dados:list):
        print(f'Enviei {dados}')
        #self.recebe_tabuleiro(self.c.desafio_atuante)
        self.envia_mensagem(self.c.desafio_atuante, dados[-1])
    
    def atraso(self, dados: list) -> None:
        print(f' Comandos().atraso: Enviei {dados}')
        self.envia_mensagem(self.c.skt,self.constroi_pacote(ATRASO,dados))
        resultado, msg = self.recebe_mensagem(self.c.skt)

    def encerra(self, dados: list) -> None:
        print(f' Comandos().encerra: Enviei {dados}')
        self.envia_mensagem(self.c.skt,self.constroi_pacote(ENCERRA,[self.c.usuario]))
        resultado, msg = self.recebe_mensagem(self.c.skt)
        if self.c.estado == DESAFIANDO:
            self.c.interpretador[C_MOVE] = self.move
        if resultado == True:
            self.c.estado = CONECTADO
    
    def sai(self, dados: list) -> None:
        print(f' Comandos().sai: Enviei {dados}')
        self.envia_mensagem(self.c.skt,self.constroi_pacote(SAI,[self.c.usuario]))
        resultado, msg = self.recebe_mensagem(self.c.skt)
        if resultado == True:
            self.c.estado = NEUTRO
    
    def tchau(self, dados: list) -> None:
        print(f' Comandos().tchau: Enviei {dados}')
        self.envia_mensagem(self.c.skt,self.constroi_pacote(TCHAU,[self.c.usuario]))
        resultado, msg = self.recebe_mensagem(self.c.skt)
        exit()

    def envia_tabuleiro(self, skt: socket):  
        self.envia_mensagem(skt,json.dumps(self.c.pacman._tabuleiro))
        
    def recebe_tabuleiro(self, skt: socket):
        resultado, msg = self.recebe_mensagem(skt)
        self.c.pacman = Pacman(json.loads(msg))

    def processa_resultado_do_jogo():
        pass

    def envia_mensagem(self, skt: socket, mensagem: str):
        #print(f' [+] Comandos().envia_mensagem: Enviei {mensagem}')
        skt.sendall(bytearray(mensagem.encode(encoding='utf-8')))

    def recebe_mensagem(self, skt: socket):
        msg = skt.recv(BUFFER_SIZE).decode('utf-8')
        msg = msg.replace(HEARTBEAT,'')
        if msg == ACK:
            #print(f' [+] Comandos().recebe_mensagem: Recebi ACK')
            return True, msg
        else:
            #print(f' [-] Comandos().recebe_mensagem: Não recebi ACK')
            return False, msg
        
    #def heartbeat(self):
    #    self.envia_mensagem(self.c.skt,ACK)
        
    #def verifica_pacotes_servidor_recebidos(self):
    #    #setblocking permite que seja feito a leitura do buffer do socket sem que haja a interrupção do fluxo do programa até que haja algo para ser lido
    #    self.c.skt.setblocking(0)
    #    try:
    #        resultado, msg = self.recebe_mensagem(self.c.skt)
    #        print(f' [+] Comandos().verifica_pacotes_recebidos: {resultado}, {msg}')
    #        self.heartbeat()
    #    except BlockingIOError:
    #        print(f' [+] Comandos().verifica_pacotes_recebidos: Nada recebido')
    #    self.c.skt.setblocking(1)
        
    def verifica_pacotes_desafiante(self):
        if self.c.desafio_atuante != None:
            self.c.desafio_atuante.setblocking(0)
            try:
                data = self.recebe_mensagem(self.c.desafio_atuante)
                self.envia_mensagem(self.c.desafio_atuante, HELLO)
                print(data)
            except BlockingIOError:
                pass
            self.c.desafio_atuante.setblocking(0)    
    
class Cliente():
    desafio_atuante = None
    def __init__(self) -> None:
        self.comandos = Comandos(self)
        self.estado = NEUTRO
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
            C_TCHAU: self.comandos.tchau,
        }
        self.comandos_do_estado = {
            NEUTRO: [C_NOVO, C_ENTRA, C_TCHAU],
            CONECTADO: [C_SENHA, C_LIDERES, C_LISTA, C_INICIA, C_DESAFIO, C_SAI],
            JOGANDO: [C_MOVE, C_ATRASO, C_ENCERRA],
            DESAFIANDO : [C_ATRASO, C_ENCERRA]
        }

    def processa_cliente(self):
        while True:
            #self.comandos.verifica_pacotes_desafiante()
            comando = input(PROMPT)
            if self.comando_valido(comando):
                acao = comando.split()[0]
                argumentos = comando.split()[1:]
                if acao in self.comandos_do_estado[self.estado]:
                    print(f' [+] Cliente().processa_cliente: Recebi o comando {acao} com argumentos {argumentos}')
                    self.interpretador[acao](argumentos)
        
    def comando_valido(self, comando):
        for valido in comandos_validos:
            if valido in comando:
                return True
            
    def desafio_escuta_background(self):
        self.desafio_ouvinte.listen()
        while True:
            conn, addr = self.desafio_ouvinte.accept()
            if conn:
                self.desafio_atuante = conn
                self.comandos.envia_tabuleiro(conn)
            if self.desafio_atuante != None:
                self.desafio_ouvinte.close()
                break

    def configura_desafio_ouvinte(self):
        self.desafio_ouvinte = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.desafio_ouvinte.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #?
        self.desafio_ouvinte.bind((host,self.skt.getsockname()[1]+CONSTANTE)) 
        desafio_thread = Thread(target=self.desafio_escuta_background)
        desafio_thread.start()
    
class ClienteTCP(Cliente):
    _estado = None
    def __init__(self, host, port) -> None:
        super().__init__()
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #?
        self.skt.bind((host,port))
        self.configura_desafio_ouvinte()
        print(self.usuario, self.senha, self.latencia, self.heartbeat)
        print(f' [+] ClienteTCP().__init__: {self.skt.getsockname()}')
        print(f' [+] ClienteTCP().__init__: {self.desafio_ouvinte.getsockname()}')

    def conecta_com_servidor(self, serv_host, serv_port):
        #self.serv_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skt.connect((serv_host, int(serv_port)))
        self.skt.sendall(bytearray(HELLO.encode(encoding='utf-8')))
        msg = self.skt.recv(BUFFER_SIZE).decode('utf-8')
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
        dummy, host, port, tipo = ['dummy',HOST,0,'TCP']
    c = ''
    if tipo == 'TCP':
        c = ClienteTCP(host, port)
    elif tipo == 'UDP':
        c = ClienteUDP(host, port)
    else:
        c = ClienteTCP(host, port)
    c.conecta_com_servidor(HOST, 6969)

    