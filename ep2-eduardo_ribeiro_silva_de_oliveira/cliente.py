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


class Cliente():
    desafio_atuante = None
    def __init__(self) -> None:
        
        self.estado = NEUTRO
        self.usuario = 'u'
        #self.senha = 's'
        self.pontuacao = 0
        self.latencia = []
        self.heartbeat = [] 
        self.pacman = Pacman(ESTADO_INICIAL)
        self.interpretador = {
            C_NOVO: self.novo,
            C_SENHA: self.senha,
            C_ENTRA: self.entra,
            C_LIDERES: self.lideres,
            C_LISTA:  self.l,
            C_INICIA: self.inicia,
            C_DESAFIO: self.desafio,
            C_MOVE: self.move,
            C_ATRASO: self.atraso,
            C_ENCERRA: self.encerra,
            C_SAI: self.sai,
            C_TCHAU: self.tchau
        }
        self.comandos_do_estado = {
            NEUTRO: [C_NOVO, C_ENTRA, C_TCHAU],
            CONECTADO: [C_SENHA, C_LIDERES, C_LISTA, C_INICIA, C_DESAFIO, C_SAI],
            JOGANDO: [C_MOVE, C_ATRASO, C_ENCERRA],
            DESAFIANDO : [C_ATRASO, C_ENCERRA]
        }

    def processa_cliente(self):
        while True:
            comando = input(PROMPT)
            if self.comando_valido(comando):
                acao = comando.split(' ')[0]
                argumentos = comando.split()[1:]
                if acao in self.comandos_do_estado[self.estado]:
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
                self.envia_tabuleiro(conn)
            if self.desafio_atuante != None:
                self.desafio_ouvinte.close()
                break

    def configura_desafio_ouvinte(self):
        self.desafio_ouvinte = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.desafio_ouvinte.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #?
        self.desafio_ouvinte.bind((host,self.skt.getsockname()[1]+CONSTANTE)) 
        desafio_thread = Thread(target=self.desafio_escuta_background)
        desafio_thread.start()
    
    def constroi_pacote(self, tipo, argumentos: list):
        string = tipo
        for item in argumentos:
            string+= str(len(item))+item
        return string

    def novo(self, argumentos: list) -> None:
        self.envia_mensagem(self.skt,self.constroi_pacote(NOVO, argumentos))
        resultado, msg = self.recebe_mensagem(self.skt)

    def senha(self, dados: list) -> None:
        self.envia_mensagem(self.skt,self.constroi_pacote(SENHA, [self.usuario]+dados))
        resultado, msg = self.recebe_mensagem(self.skt)
    
    def entra(self, dados: list) -> None:
        self.envia_mensagem(self.skt,self.constroi_pacote(ENTRA,dados))
        resultado, msg = self.recebe_mensagem(self.skt)
        if resultado == True:
            self.usuario = dados[0]
            self.senha = dados[1]
            self.estado = CONECTADO

    def lideres(self, dados: list) -> None:
        self.envia_mensagem(self.skt,self.constroi_pacote(LIDERES,dados))
        resultado, msg = self.recebe_mensagem(self.skt)
    
    def l(self,dados: list) -> None:
        self.envia_mensagem(self.skt,self.constroi_pacote(LISTA_CONECTADOS,dados))
        resultado, msg = self.recebe_mensagem(self.skt)
        if resultado == False:
            print(f'{PROMPT} CONECTADOS:')
            for index, linha in enumerate(msg.split('\n')[:-1]):
                print(f'       >[{index}]: {linha}')
    
    def inicia(self,dados: list) -> None:
        self.envia_mensagem(self.skt,self.constroi_pacote(INICIA,[self.usuario]))
        resultado, msg = self.recebe_mensagem(self.skt)
        if resultado == True:
            self.estado = JOGANDO
            self.pacman.mostra_tabuleiro()
            
    
    def desafio(self, dados: list) -> None:
        self.envia_mensagem(self.skt,self.constroi_pacote(DESAFIO,dados))
        resultado, msg = self.recebe_mensagem(self.skt)
        if not resultado:
            host,port = msg.split()
            port = int(port)+CONSTANTE
            self.desafio_atuante = socket.socket()
            self.desafio_atuante.connect((host,port))
            self.desafio_ouvinte.close()
            self.estado = DESAFIANDO
            self.recebe_tabuleiro(self.desafio_atuante)
            self.processa_desafio()
            
    
    def processa_desafio(self):
        msg = ''
        while msg != 'encerra':
            anterior = self.pacman._tabuleiro 
            while anterior == self.pacman._tabuleiro:
                self.recebe_tabuleiro(self.desafio_atuante)
            self.pacman.mostra_tabuleiro()
            msg = input(f'{PROMPT}').split(' ')
            if msg == ['encerra']:
                self.move_remoto([NACK])
                self.desafio_atuante.close()
                self.desafio_atuante = None
                break
            else:
                self.move_remoto(msg)
        self.processa_cliente()
            

    def move(self, dados: list) -> None:
        self.pacman.mostra_tabuleiro()
        self.pacman.movimenta_fantasmas_locais()
        self.pacman.colisao_fantasma_local()
        time.sleep(1)
        self.pacman.mostra_tabuleiro()
        if self.desafio_atuante != None:
            self.envia_tabuleiro(self.desafio_atuante)
            resultado, direcao = self.recebe_mensagem(self.desafio_atuante)
            if direcao != NACK:
                self.pacman.movimenta_fantasma_remoto(direcao)
                self.pacman.colisao_fantasma_remoto()
            else:
                self.desafio_atuante.close()
                self.desafio_atuante = None
            time.sleep(1)
            self.pacman.mostra_tabuleiro()
        self.pacman.movimenta_pacman(dados[0])
        self.pacman.colisao_pacman()
        time.sleep(1)
        self.pacman.mostra_tabuleiro()
    
    def move_remoto(self, dados:list):
        self.envia_mensagem(self.desafio_atuante, dados[-1])
    
    def atraso(self, dados: list) -> None:
        self.envia_mensagem(self.skt,self.constroi_pacote(ATRASO,dados))
        resultado, msg = self.recebe_mensagem(self.skt)

    def encerra(self, dados: list) -> None:
        self.envia_mensagem(self.skt,self.constroi_pacote(ENCERRA,[self.usuario]))
        resultado, msg = self.recebe_mensagem(self.skt)
        if self.estado == DESAFIANDO:
            self.interpretador[C_MOVE] = self.move
        if resultado == True:
            self.estado = CONECTADO
    
    def sai(self, dados: list) -> None:
        self.envia_mensagem(self.skt,self.constroi_pacote(SAI,[self.usuario]))
        resultado, msg = self.recebe_mensagem(self.skt)
        if resultado == True:
            self.estado = NEUTRO
    
    def tchau(self, dados: list) -> None:
        self.envia_mensagem(self.skt,self.constroi_pacote(TCHAU,[self.usuario]))
        resultado, msg = self.recebe_mensagem(self.skt)
        exit()

    def envia_tabuleiro(self, skt: socket):  
        self.envia_mensagem(skt,json.dumps(self.pacman._tabuleiro))
        
    def recebe_tabuleiro(self, skt: socket):
        resultado, msg = self.recebe_mensagem(skt)
        self.pacman = Pacman(json.loads(msg))

    def processa_resultado_do_jogo():
        pass

    def envia_mensagem(self, skt: socket, mensagem: str):
        skt.sendall(bytearray(mensagem.encode(encoding='utf-8')))

    def recebe_mensagem(self, skt: socket):
        msg = skt.recv(BUFFER_SIZE).decode('utf-8')
        msg = msg.replace(HEARTBEAT,'')
        if msg == ACK:
            return True, msg
        else:
            return False, msg


class ClienteTCP(Cliente):
    _estado = None
    def __init__(self, host, port) -> None:
        super().__init__()
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #?
        self.skt.bind((host,port))
        self.configura_desafio_ouvinte()

    def conecta_com_servidor(self, serv_host, serv_port):
        self.skt.connect((serv_host, int(serv_port)))
        self.skt.sendall(bytearray(HELLO.encode(encoding='utf-8')))
        msg = self.skt.recv(BUFFER_SIZE).decode('utf-8')
        if msg == HELLO:
            self.processa_cliente()
        else:
            exit()

class ClienteUDP(Cliente):
    _estado = None
    
    def __init__(self, host, port) -> None:
        super().__init__()
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #?
        self.skt.bind((host,port))
        self.configura_desafio_ouvinte()

    def conecta_com_servidor(self, serv_host, serv_port):
        self.serverAddress = (serv_host, serv_port)
        self.envia_mensagem(self.skt,HELLO)
        resultado, msg = self.recebe_mensagem(self.skt)
        if msg == HELLO:
            self.processa_cliente()
        else:
            exit()

    def envia_mensagem(self, skt: socket, mensagem: str):
        skt.sendto(bytearray(mensagem.encode(encoding='utf-8')),self.serverAddress)

if __name__ == '__main__':
    try:
        dummy, host, port, tipo = sys.argv
    except:
        dummy, host, port, tipo = ['dummy',HOST,0,'UDP']
    c = ''
    if tipo == 'TCP':
        c = ClienteTCP(HOST, 0)
    elif tipo == 'UDP':
        c = ClienteUDP(HOST, 0)
    else:
        c = ClienteTCP(HOST, 0)
    c.conecta_com_servidor(HOST, int(port))

    










    #COMPORTAMENTOS
    #NO verificação periódica iniciada pelo servidor, de que os clientes continuam conectados.
    #NO verificação periódica entre clientes, da latencia entre eles durante uma partida;
    #OK envio das credenciais de usuario e senha em texto plano;
    #OK troca de mensagens em modo texto entre cliente e servidor e entre clientes.
    #NO reiniciar ouvinte apos encerra do move remoto
    #NO reconexao
    #NO tolerancia a falhas

    #COMANDOS
    #OK criar usuário
    #OK login
    #OK mudança de senha
    #OK logout
    #OK lista de conectados
    #OK inicio de partida
    #OK desafio
    #OK movimentação do pacman
    #OK encerramento da partida
    #OK recebimento da arena atualizada
    #NO envio do resultado da partida para o servidor
    #NO classificação dos usuários existente

    #LOGS
    #OK Servidor iniciado -> Não checa se foi finalizado corretamente 
    #OK Conexao realizada por um cliente (Enderec ̧o IP do cliente);
    #OK Login com sucesso ou nao (Nome do usuario que conseguiu, ou nao, logar, e endereco IP de onde veio o login);
    #OK Desconexao realizada por um cliente (Enderecoo IP do cliente);
    #OK Inicio de uma partida (Endereco IP e nome do usu ́ario);
    #NO Entrada e sa ́ıda de fantasma da partida existente (Enderec ̧o IP e nome do usu ́ario)
    #NO Finalizacao de uma partida (Enderec ̧os IP, nomes dos usu ́arios e nome do vencedor);
    #NO Desconex ̃ao inesperada de um cliente, verificada pelos heartbeats (Enderec ̧o IP do cliente);
    #OK Servidor finalizado