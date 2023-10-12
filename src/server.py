from __future__ import annotations
import socket  # https://docs.python.org/3/library/socket.html
import os  # https://docs.python.org/3/library/os.html
import typing  # https://docs.python.org/3/library/typing.html
import threading  # https://docs.python.org/3/library/threading.html
from abc import ABC
# CONSTANTES

HOST = 'localhost'
PORT = 6969
HEARTBEAT_TIMEOUT = 80085
SSL_TIMEOUT = 455
BUFFER_SIZE = 4096


class Logs:

    def __init__(self):
        pass

    def logs_insere_nova_mensagem(self, mensagem: Mensagens):
        pass


class Mensagens(ABC):

    def __init__(self):
        pass

    def mensagens_servidor_iniciado(self, dados: list) -> Mensagens:
        pass

    def mensagens_conexao_realizada(self, dados: list) -> Mensagens:
        pass

    def mensagens_login_sucesso(self, dados: list) -> Mensagens:
        pass

    def mensagens_login_falha(self, dados: list) -> Mensagens:
        pass

    def mensagens_inicio_de_partida(self, dados: list) -> Mensagens:
        pass

    def mensagens_fantasma_entrou(self, dados: list) -> Mensagens:
        pass

    def mensagens_fantasma_saiu(self, dados: list) -> Mensagens:
        pass

    def mensagens_finalizacao_partida(self, dados: list) -> Mensagens:
        pass

    def mensagens_desconexao_inesperada_cliente(self, dados: list) -> Mensagens:
        pass

    def mensagens_servidor_finalizado(self, dados: list) -> Mensagens:
        pass


class Usuarios:

    def __init(self):
        pass

    def usuarios_cria_novo_usuario(self, dados: list) -> None:
        pass

    def usuarios_altera_senha_do_usuario(self, dados: list) -> None:
        pass

    # def usuarios_lista_usuarios_por_pontuacao(self) -> None:
    #    pass

    # def usuarios_lista_usuarios_conectados(self) -> None:
    #    pass

    def usuarios_invade_partida(self, dados: list) -> None:
        pass


class Logados:
    def __init__(self):
        pass

    def logados_adiciona_usuario(self, dados: list) -> None:
        pass

    def logados_remove_usuario(self, dados: list) -> None:
        pass

    def logados_retorna_listagem(self, dados: list) -> None:
        pass


class Pontuacoes:
    def __init__(self):
        pass

    def pontuacoes_adiciona_usuario(self, dados: list) -> None:
        pass

    def pontuacoes_atualiza_dados(self, dados: list) -> None:
        pass

    def pontuacoes_retorna_listagem(self, dados: list) -> None:
        pass


class ClientesTCP:
    def __init__(self):
        pass

    def clientes_tcp_faz_leitura(self, dados: list) -> None:
        pass

    def clientes_tcp_faz_escrita(self, dados: list) -> None:
        pass

    def clientes_tcp_interpreta_pacote(self, dados: list) -> None:
        pass


class ClientesUDP:
    def __init__(self):
        pass

    def clientes_udp_faz_leitura(self, dados: list) -> None:
        pass

    def clientes_udp_faz_escrita(self, dados: list) -> None:
        pass

    def clientes_udp_interpreta_pacote(self, dados: list) -> None:
        pass


class Auxiliares:

    def __init__(self):
        pass

    def auxiliares_cria_listener_UDP(self, dados: list):
        pass

    def auxiliares_cria_listener_TCP(self, dados: list):
        pass

    def auxiliares_envia_desafio(self, dados: list):
        pass

    def auxiliares_envia_mensagem_para_socket(self, dados: list):
        pass


if __name__ == '__main__':
    print('Olá, mundo!')
