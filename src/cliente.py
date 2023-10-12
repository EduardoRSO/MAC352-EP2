from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List


class Comandos(ABC):
    @abstractmethod
    def comandos_novo(self, dados: list) -> None:
        pass

    @abstractmethod
    def comandos_senha(self, dados: list) -> None:
        pass

    @abstractmethod
    def comandos_entra(self, dados: list) -> None:
        pass

    @abstractmethod
    def comandos_lideres(self) -> None:
        pass

    @abstractmethod
    def comandos_l(self) -> None:
        pass

    @abstractmethod
    def comandos_inicia(self) -> None:
        pass

    @abstractmethod
    def comandos_desafio(self, dados: list) -> None:
        pass

    @abstractmethod
    def comandos_move(self, dados: list) -> None:
        pass

    @abstractmethod
    def comandos_atraso(self) -> None:
        pass

    @abstractmethod
    def comandos_encerra(self) -> None:
        pass

    @abstractmethod
    def comandos_sai(self) -> None:
        pass

    @abstractmethod
    def comandos_tchau(self) -> None:
        pass


class Estados(Comandos, ABC):

    @property
    def cliente(self) -> Clientes:
        return self._cliente

    @cliente.setter
    def cliente(self, cliente: Clientes) -> None:
        self._cliente = cliente

    def executa_comando(self, dados: list):
        pass


class EstadosNeutro(Estados):  # novo entra lideres l tchau

    def comandos_novo(self, dados: list) -> None:
        pass

    def comandos_senha(self, dados: list) -> None:
        pass

    def comandos_entra(self, dados: list) -> None:
        pass

    def comandos_lideres(self) -> None:
        pass

    def comandos_l(self) -> None:
        pass

    def comandos_inicia(self) -> None:
        pass

    def comandos_desafio(self, dados: list) -> None:
        pass

    def comandos_move(self, dados: list) -> None:
        pass

    def comandos_atraso(self) -> None:
        pass

    def comandos_encerra(self) -> None:
        pass

    def comandos_sai(self) -> None:
        pass

    def comandos_tchau(self) -> None:
        pass

    def executa_comando(self, dados: list):
        pass


class EstadosConectado(Estados):  # senha lideres l inicia desafio sai

    def comandos_novo(self, dados: list) -> None:
        pass

    def comandos_senha(self, dados: list) -> None:
        pass

    def comandos_entra(self, dados: list) -> None:
        pass

    def comandos_lideres(self) -> None:
        pass

    def comandos_l(self) -> None:
        pass

    def comandos_inicia(self) -> None:
        pass

    def comandos_desafio(self, dados: list) -> None:
        pass

    def comandos_move(self, dados: list) -> None:
        pass

    def comandos_atraso(self) -> None:
        pass

    def comandos_encerra(self) -> None:
        pass

    def comandos_sai(self) -> None:
        pass

    def comandos_tchau(self) -> None:
        pass

    def executa_comando(self, dados: list):
        pass


class EstadosJogando(Estados):  # lideres l move atraso encerra

    def comandos_novo(self, dados: list) -> None:
        pass

    def comandos_senha(self, dados: list) -> None:
        pass

    def comandos_entra(self, dados: list) -> None:
        pass

    def comandos_lideres(self) -> None:
        pass

    def comandos_l(self) -> None:
        pass

    def comandos_inicia(self) -> None:
        pass

    def comandos_desafio(self, dados: list) -> None:
        pass

    def comandos_move(self, dados: list) -> None:
        pass

    def comandos_atraso(self) -> None:
        pass

    def comandos_encerra(self) -> None:
        pass

    def comandos_sai(self) -> None:
        pass

    def comandos_tchau(self) -> None:
        pass

    def executa_comando(self, dados: list):
        pass


class Clientes:
    _estado = None

    def __init__(self, estado: Estados) -> None:
        self.clientes_transiciona_para(estado)

    def clientes_transiciona_para(self, estado: Estados) -> None:
        self._estado = estado
        self._estado.cliente = self

    def clientes_executa_comando(self, dados: list) -> None:
        self._estado.executa_comando(dados)


if __name__ == '__main__':
    print('Olá, mundo!')
