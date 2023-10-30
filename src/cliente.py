from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
import sys
import pacman

NOVO = '0'
SENHA = '1'
ENTRA = '2'
LIDERES='3'
LISTA_CONECTADOS = '4'
LISTA_TODOS = '5'
INICIA= '6'
DESAFIO = '7'
DESLOGA = '8'
MOVE = '9'
ATRASO = '10'
ENCERRA  ='11'
TCHAU = '12'
TABULEIRO = '13'

class Comandos(ABC):
    @abstractmethod
    def novo(self, dados: list) -> None:
        pass

    @abstractmethod
    def senha(self, dados: list) -> None:
        pass

    @abstractmethod
    def entra(self, dados: list) -> None:
        pass

    @abstractmethod
    def lideres(self) -> None:
        pass

    @abstractmethod
    def l(self) -> None:
        pass

    @abstractmethod
    def inicia(self) -> None:
        pass

    @abstractmethod
    def desafio(self, dados: list) -> None:
        pass

    @abstractmethod
    def move(self, dados: list) -> None:
        pass

    @abstractmethod
    def atraso(self) -> None:
        pass

    @abstractmethod
    def encerra(self) -> None:
        pass

    @abstractmethod
    def sai(self, dados: list) -> None:
        pass

    @abstractmethod
    def tchau(self) -> None:
        pass

class Estados(Comandos, ABC):

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @cliente.setter
    def cliente(self, cliente: Cliente) -> None:
        self._cliente = cliente

    def executa_comando(self, dados: list):
        pass

class EstadosNeutro(Estados):  # novo entra lideres l tchau

    def novo(self, dados: list) -> None:
        usuario,senha = dados
        return f'{NOVO}{len(usuario)}{usuario}{len(senha)}{senha}'

    def senha(self, dados: list) -> None:
        pass

    def entra(self, dados: list) -> None:
        usuario, senha = dados
        return f'{ENTRA}{len(usuario)}{usuario}{len(senha)}{senha}'

    def lideres(self) -> None:
        return f'{LIDERES}'

    def l(self) -> None:
        return f'{LISTA_CONECTADOS}'

    def inicia(self) -> None:
        pass

    def desafio(self, dados: list) -> None:
        pass

    def move(self, dados: list) -> None:
        pass

    def atraso(self) -> None:
        pass

    def encerra(self) -> None:
        pass

    def sai(self, dados: list) -> None:
        pass

    def tchau(self) -> None:
        return f'{TCHAU}'

    def executa_comando(self, dados: list):
        pass

class EstadosConectado(Estados):  # senha lideres l inicia desafio sai

    def novo(self, dados: list) -> None:
        pass

    def senha(self, dados: list) -> None:
        usuario, senha_antiga, senha_nova = dados
        return f'{SENHA}{len(usuario)}{usuario}{len(senha_antiga)}{senha_antiga}{len(senha_nova)}{senha_nova}'

    def entra(self, dados: list) -> None:
        pass

    def lideres(self) -> None:
        return f'{LIDERES}'

    def l(self) -> None:
        return f'{LISTA_CONECTADOS}'

    def inicia(self) -> None:
        return f'{INICIA}'

    def desafio(self, dados: list) -> None:
        usuario = dados
        return f'{DESAFIO}{len(usuario)}{usuario}'

    def move(self, dados: list) -> None:
        pass

    def atraso(self) -> None:
        pass

    def encerra(self) -> None:
        pass

    def sai(self, dados: list) -> None:
        usuario = dados
        return f'{DESLOGA}{len(usuario)}{usuario}'

    def tchau(self) -> None:
        pass

    def executa_comando(self, dados: list):
        pass

class EstadosJogando(Estados):  # move atraso encerra

    def novo(self, dados: list) -> None:
        pass

    def senha(self, dados: list) -> None:
        pass

    def entra(self, dados: list) -> None:
        pass

    def lideres(self) -> None:
        pass

    def l(self) -> None:
        pass

    def inicia(self) -> None:
        pass

    def desafio(self, dados: list) -> None:
        pass

    def move(self, dados: list) -> None:
        direcao = dados
        return f'{MOVE}{len(direcao)}{direcao}'

    def atraso(self) -> None:
        return f'{ATRASO}'    

    def encerra(self) -> None:
        return f'{ENCERRA}'

    def sai(self, dados: list) -> None:
        pass

    def tchau(self) -> None:
        pass

    def executa_comando(self, dados: list):
        pass

class Cliente:
    _estado = None

    def __init__(self, estado: Estados) -> None:
        self.clientes_transiciona_para(estado)

    def clientes_transiciona_para(self, estado: Estados) -> None:
        self._estado = estado
        self._estado.cliente = self

    def clientes_executa_comando(self, dados: list) -> None:
        self._estado.executa_comando(dados)

    #pacman deve ter um método que transcreve o tabuleiro para uma string
    #pacman deve ser instanciado ao receber um tabuleiro em lista
    #talvez o init do pacman nao deva ser o jogo propriamente dito
    #se eu fizer um método que de fato inicia, eu conseguiria modularizar o codigo
    #para obter o comportamento de que um cliente tem uma instancia de pacman
    #mas o jogo só começa quando ele faz uma chamada do metodo start_game. 
    # Esse start game que receberia o tabuleiro em lista.
    #essa separação seria apenas para que eu pudesse utilizar os métodos 
    #serializa_tabuleiro e deserializa_tabuleiro...
    def envia_tabuleiro(self, dados: list):  
        #return f'{TABULEIRO}{linhas}{colunas}{tabuleiro_to_str}'
        pass

    def recebe_tabuleiro(self, dados: list):
        pass

class ClienteTCP(Cliente):
    _estado = None
    def __init__(self, host, port) -> None:
        super().__init__(EstadosNeutro())
        self._host = host
        self._port = port
        self._usuario = 'u'
        self._senha = 's'
        self._latencia = []
        self._heartbeat = []
        print(self._estado, self._host, self._port, self._usuario, self._senha, self._latencia, self._heartbeat)
    

class ClienteUDP(Cliente):
    pass

if __name__ == '__main__':
    dummy, host, port, tipo = sys.argv
    c = ''
    if tipo == 'TCP':
        c = ClienteTCP(host, port)
    elif tipo == 'UDP':
        c = ClienteUDP(host, port)
    else:
        c = ClienteTCP(host, port)

    