from array import *
import random

PAREDE = '*'
PONTO= '.'
VAZIO = ' '
FANSTASMA_LOCAL = 'F'
FANSTASMA_REMOTO = 'f'
SOBREPOSICAO = 'H'
PACMAN = 'C'
NUMERO_DE_FANTASMAS = 3

movimentos = {
    'UP': tuple((-1,0)),
    'DOWN':tuple((1,0)),
    'LEFT': tuple((0,-1)),
    'RIGHT': tuple((0,1))
}

ESTADO_INICIAL = [
[PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PONTO,PAREDE,PAREDE,PONTO,PONTO,PONTO,VAZIO,PONTO,PONTO,PONTO,PONTO,PONTO,PAREDE,PAREDE,PONTO,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE],
[PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PONTO,PAREDE,PAREDE,PONTO,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PONTO,PAREDE,PAREDE,PONTO,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE],
[PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PONTO,PAREDE,PAREDE,PONTO,PAREDE,PONTO,PONTO,VAZIO,PONTO,PONTO,PAREDE,PONTO,PAREDE,PAREDE,PONTO,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE],
[PONTO,PONTO,PONTO,PONTO,PONTO,VAZIO,PONTO,PONTO,PONTO,PONTO,PAREDE,PONTO,PONTO,PONTO,PONTO,PONTO,PAREDE,PONTO,PONTO,PONTO,PONTO,PONTO,PONTO,PONTO,'F',PONTO,PONTO],
[PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PONTO,PAREDE,PAREDE,PONTO,PAREDE,PONTO,PONTO,VAZIO,PONTO,PONTO,PAREDE,PONTO,PAREDE,PAREDE,PONTO,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,PAREDE,]
]

class Tabuleiro:
    def __init__(self, estado: list[list[str]],  posicao: tuple, simbolo: str) -> None:
        self._tabuleiro = estado
        self._linhas = len(estado)-1
        self._colunas = len(estado[0])-1 
        self._posicao = posicao
        self._posicao_inicial = posicao
        self._simbolo = simbolo
        self._fantasmas_locais = self.inicia_fantasmas_locais()
        self._fantasma_remoto = None
        self._pontuacao = 0

    def mostra_tabuleiro(self):
        print(self._pontuacao)
        for linha in self._tabuleiro:
            print(linha)

    def inicia_fantasmas_locais(self):
        self._fantasmas_locais = []
        for i in range (NUMERO_DE_FANTASMAS):
            self._fantasmas_locais.append((4,13))

    def movimenta_fantasma_local(self, posicao):
        pass

    def colisao_fantasma_local(self):
        pass

    def inicia_fantasma_remoto(self, dados: list):
        self._fantasma_remoto = dados

    def movimenta_fantasma_remoto(self):
        pass

    def colisao_fantasma_remoto(self):
        pass

    def _acessa_simbolo(self, posicao):
        return self._tabuleiro[posicao[0]][posicao[1]]

    def _atualiza_simbolo(self, posicao, simbolo):
        self._tabuleiro[self._posicao[0]][self._posicao[1]] = simbolo

    def _limite_vertical(self, posicao: tuple):
        return posicao[0] > self._linhas or posicao[0] < 0 
    
    def _limite_horizontal(self, posicao:tuple):
        return posicao[1] > self._colunas or posicao[1] < 0
    
    def _eh_parede(self, posicoes: list):
        for posicao in posicoes:
            if self._acessa_simbolo(posicao) != PAREDE:
                return False
        return True
    
    def _move_para(self, posicao, simbolo):
        self._atualiza_simbolo(self._posicao, simbolo)
        self._posicao = posicao

    def movimenta_pacman(self, direcao: tuple):
        posicao = (self._posicao[0]+direcao[0],self._posicao[1]+ direcao[1])
        if self._limite_vertical(posicao):
            if not self._eh_parede([(0,posicao[1]), (self._linhas, posicao[1])]):
                self._move_para((0,posicao[1]), VAZIO) if posicao[0] > self._linhas else self._move_para((self._linhas, posicao[1]), VAZIO)
        elif self._limite_horizontal(posicao):
            if not self._eh_parede([(posicao[0],0), (posicao[0], self._colunas)]):
                self._move_para((posicao[0],0),VAZIO) if posicao[1] > self._colunas else self._move_para((posicao[0], self._colunas), VAZIO)
        elif not self._eh_parede([posicao]):
                self._move_para(posicao, VAZIO)
                
    def colisao_pacman(self):
        objeto = self._acessa_simbolo(self._posicao)
        if objeto == PONTO:
            self._pontuacao += 1 
        elif objeto in [SOBREPOSICAO, FANSTASMA_REMOTO, FANSTASMA_LOCAL]:
            self._move_para(self._posicao_inicial, objeto)
        self._atualiza_simbolo(self._posicao, self._simbolo)
            

    def movimenta(self, direcao):
        #self.movimenta_fantasma_local()
        #self.colisao_fantasma_local()
        
        self.movimenta_fantasma_remoto()
        self.colisao_fantasma_remoto()
        
        self.movimenta_pacman(direcao)
        self.colisao_pacman()
        
        self.mostra_tabuleiro()






if __name__ == '__main__':
    T = Tabuleiro(ESTADO_INICIAL, tuple((3,6)), PACMAN)
    print('Olá, mundo!')
    while True:
        x = input('') 
        try:
            T.movimenta(movimentos[x.upper()])
        except:
            continue