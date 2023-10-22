from array import *
import random

PAREDE = '*'
PONTO= '.'
VAZIO = ' '
FANSTASMA_LOCAL = 'F'
FANSTASMA_REMOTO = 'f'
SOBREPOSICAO = 'H'
PACMAN = 'C'
NUMERO_DE_FANTASMAS = 4
SPAWN_PACMAN = (3, 1)
SPAWN_FANSTASMA_LOCAL = [(3,13), (3,13), (3,13), (3,13)]
SPAWN_FANTASMA_REMOTO = (2, 13)

movimentos = {
    'UP': tuple((-1,0)),
    'DOWN':tuple((1,0)),
    'LEFT': tuple((0,-1)),
    'RIGHT': tuple((0,1))
}

ESTADO_INICIAL = [
[[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PONTO],[PAREDE],[PAREDE],[PONTO],[PONTO],[PONTO],[VAZIO],[PONTO],[PONTO],[PONTO],[PONTO],[PONTO],[PAREDE],[PONTO],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE]],
[[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PONTO],[PAREDE],[PAREDE],[PONTO],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PONTO],[PAREDE],[PAREDE],[PONTO],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE]],
[[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PONTO],[PAREDE],[PAREDE],[PONTO],[PAREDE],[PONTO],[PONTO],['f'],[PONTO],[PONTO],[PAREDE],[PONTO],[PAREDE],[PAREDE],[PONTO],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE]],
[[PONTO],[PACMAN],[PONTO],[PONTO],[PONTO],[VAZIO],[PONTO],[PONTO],[PONTO],[PONTO],[PAREDE],[PONTO],[PONTO],[PONTO],[PONTO],[PONTO],[PAREDE],[PONTO],[PONTO],[PONTO],[PONTO],[PONTO],[PONTO],[PONTO],[PONTO],[PONTO],[PONTO]],
[[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PONTO],[PAREDE],[PAREDE],[PONTO],[PAREDE],[PONTO],[PONTO],['F','F','F','F'],[PONTO],[PONTO],[PAREDE],[PONTO],[PAREDE],[PAREDE],[PONTO],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE],[PAREDE]]
]


class Tabuleiro:
    def __init__(self, estado) -> None:
        self._tabuleiro = estado
        self._linhas = len(estado)-1
        self._colunas = len(estado[0])-1 
        self._posicao_pacman = SPAWN_PACMAN if self._encontra_no_tabuleiro(PACMAN) == None else self._encontra_no_tabuleiro(PACMAN)
        self._posicao_fantasmas_locais = self._encontra_fantasmas_no_tabuleiro()
        self._posicao_fantasma_remoto = SPAWN_FANTASMA_REMOTO if self._encontra_no_tabuleiro(FANSTASMA_REMOTO) == None else self._encontra_no_tabuleiro(FANSTASMA_REMOTO) 
        self._pontuacao = 0

    #----------------------------------------------------
    def _encontra_no_tabuleiro(self, simbolo):
        for i in range(self._linhas):
            for j in range(self._colunas):
                if simbolo in self._tabuleiro[i][j]:
                    return (i,j)
        return None
    
    def _encontra_fantasmas_no_tabuleiro(self):
        posicoes = []
        i = 0
        for linha in self._tabuleiro:
            j = 0
            for coluna in linha:
                if FANSTASMA_LOCAL in coluna:
                    for _ in range(self._conta_fantasmas(coluna)):
                        posicoes.append((i,j))
                j +=1
            i +=1
        return SPAWN_FANSTASMA_LOCAL if posicoes == [] else posicoes
        
    def _conta_fantasmas(self, celula):
        contador = 0
        for item in celula:
            if item in [FANSTASMA_LOCAL, FANSTASMA_REMOTO]:
                contador+=1
        return contador

    def _acessa_simbolo(self, posicao):
        return self._tabuleiro[posicao[0]][posicao[1]][-1]
    
    def _insere_simbolo(self, posicao, simbolo):
        self._tabuleiro[posicao[0]][posicao[1]].append(simbolo)

    def _remove_simbolo(self, posicao):
        a = self._tabuleiro[posicao[0]][posicao[1]].pop()
        if len(self._tabuleiro[posicao[0]][posicao[1]]) == 0:
            self._tabuleiro[posicao[0]][posicao[1]].append(VAZIO)

    def _limite_vertical(self, posicao: tuple):
        return posicao[0] > self._linhas or posicao[0] < 0 
    
    def _limite_horizontal(self, posicao:tuple):
        return posicao[1] > self._colunas or posicao[1] < 0
    
    def _eh_parede(self, posicoes: list):
        for posicao in posicoes:
            if self._acessa_simbolo(posicao) != PAREDE:
                return False
        return True
    
    def _calcula_nova_posicao(self, posicao_antiga, direcao):
        return (posicao_antiga[0]+direcao[0],posicao_antiga[1]+direcao[1])
    #----------------------------------------------------

    def mostra_tabuleiro(self):
        print(self._pontuacao, self._posicao_pacman, self._posicao_fantasmas_locais, self._posicao_fantasma_remoto)
        for linha in self._tabuleiro:
            for coluna in linha:
                if self._conta_fantasmas(coluna) > 1:
                    print(SOBREPOSICAO, end= ' ')
                else:
                    print(coluna[-1], end=' ')
            print()
        print()
        print(self._tabuleiro)

    def movimenta_todos(self, direcao):
        self.movimenta_fantasmas_locais()
        self.colisao_fantasma_local()
        
        self.movimenta_fantasma_remoto()
        self.colisao_fantasma_remoto()
        
        self.movimenta_pacman(direcao)
        self.colisao_pacman()
        
        self.mostra_tabuleiro()    

    #invoca o método de movimento para cada posicao de fantasma local
    def movimenta_fantasmas_locais(self):
        movimentos_realizados = []
        for posicao in self._posicao_fantasmas_locais:
            direcao = movimentos[random.choice(list(movimentos.keys()))]
            movimentos_realizados.append(self.movimenta(posicao, direcao, FANSTASMA_LOCAL))
        self._posicao_fantasmas_locais = movimentos_realizados

    #invoca o método de movimento para o fantasma remoto. DEVE receber a DIRECAO
    def movimenta_fantasma_remoto(self):
        direcao = movimentos[random.choice(list(movimentos.keys()))]
        self._posicao_fantasma_remoto = self.movimenta(self._posicao_fantasma_remoto, direcao, FANSTASMA_REMOTO)

    def movimenta_pacman(self, direcao):
        self._posicao_pacman = self.movimenta(self._posicao_pacman, direcao, PACMAN)

    def movimenta(self, posicao_antiga, direcao, simbolo):
        posicao = self._calcula_nova_posicao(posicao_antiga, direcao)
        if self._limite_vertical(posicao):
            if not self._eh_parede([(0,posicao[1]), (self._linhas, posicao[1])]):
               self._remove_simbolo(posicao_antiga)
               return (0,posicao[1]) if posicao[0] > self._linhas else (self._linhas, posicao[1])
        elif self._limite_horizontal(posicao):
            if not self._eh_parede([(posicao[0],0), (posicao[0], self._colunas)]):
               self._remove_simbolo(posicao_antiga)
               return (posicao[0],0) if posicao[1] > self._colunas else (posicao[0], self._colunas)
        elif not self._eh_parede([posicao]):
               self._remove_simbolo(posicao_antiga)
               return posicao
        self._remove_simbolo(posicao_antiga)
        return posicao_antiga

    def colisao_fantasma_local(self):
        for posicao in self._posicao_fantasmas_locais:
            objeto = self._acessa_simbolo(posicao)
            if objeto == PACMAN:
                self._remove_simbolo(posicao)
                self._posicao_pacman = SPAWN_PACMAN
                self._insere_simbolo(self._posicao_pacman, PACMAN)
            self._insere_simbolo(posicao, FANSTASMA_LOCAL)

    def colisao_fantasma_remoto(self):
        objeto = self._acessa_simbolo(self._posicao_fantasma_remoto)
        if objeto == PACMAN:
            self._remove_simbolo(self._posicao_fantasma_remoto)
            self._posicao_pacman = SPAWN_PACMAN
            self._insere_simbolo(self._posicao_pacman, PACMAN)
        self._insere_simbolo(self._posicao_fantasma_remoto, FANSTASMA_REMOTO)

    def colisao_pacman(self):
        objeto = self._acessa_simbolo(self._posicao_pacman)
        if objeto == PONTO:
            self._remove_simbolo(self._posicao_pacman)
        elif objeto in [SOBREPOSICAO, FANSTASMA_REMOTO, FANSTASMA_LOCAL]:
            self._posicao_pacman = SPAWN_PACMAN
        self._insere_simbolo(self._posicao_pacman, PACMAN)






if __name__ == '__main__':
    T = Tabuleiro(ESTADO_INICIAL)
    print('Olá, mundo!')
    while True:
        T.mostra_tabuleiro()
        x = input('') 
        #try:
        T.movimenta_todos(movimentos[x.upper()])
        #except:
        #    continue