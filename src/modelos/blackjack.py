"""Lógica do Blackjack/21.


Regras implementadas:
- Jogador e dealer recebem 2 cartas; a 2ª do dealer fica virada.
- Jogador pode PEDIR, PARAR ou DOBRAR (só com 2 cartas e saldo suficiente).
- Dealer pede carta até chegar a 17 ou mais (para em qualquer 17).
- Blackjack natural (A + figura/10) paga 3:2. Empate devolve a aposta.
"""
import random
from collections import deque

NAIPES = ("copas", "ouros", "espadas", "paus")
VALORES = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")

# Fases da rodada
APOSTANDO = "apostando"
JOGADOR = "jogador"
DEALER = "dealer"
FIM = "fim"


class Carta:
    """Uma carta: valor + naipe. Os pontos e a cor são derivados."""

    def __init__(self, valor, naipe):
        if valor not in VALORES:
            raise ValueError(f"Valor inválido: {valor}")
        if naipe not in NAIPES:
            raise ValueError(f"Naipe inválido: {naipe}")
        self.valor = valor
        self.naipe = naipe

    @property
    def pontos(self):
        """Valor 'cheio': Ás conta 11 (a Mao rebaixa para 1 quando precisa)."""
        if self.valor == "A":
            return 11
        if self.valor in ("J", "Q", "K"):
            return 10
        return int(self.valor)

    @property
    def cor(self):
        return "vermelho" if self.naipe in ("copas", "ouros") else "preto"

    def __repr__(self):
        return f"Carta({self.valor} de {self.naipe})"


class Baralho:
    """Sapato com vários baralhos embaralhados.

    `cartas` permite fixar a ordem das cartas (modo teste): nesse caso
    o sapato nunca é reembaralhado e as cartas saem na ordem dada.
    """

    def __init__(self, num_baralhos=4, rng=None, cartas=None):
        self.num_baralhos = num_baralhos
        self._rng = rng or random.Random()
        self._fixo = cartas is not None
        self._cartas = deque(cartas) if self._fixo else deque()
        if not self._fixo:
            self._reabastecer()

    def _reabastecer(self):
        todas = [
            Carta(v, n)
            for _ in range(self.num_baralhos)
            for n in NAIPES
            for v in VALORES
        ]
        self._rng.shuffle(todas)
        self._cartas = deque(todas)

    def __len__(self):
        return len(self._cartas)

    def reembaralhar_se_preciso(self, minimo=15):
        """Chamado entre rodadas: evita que o sapato acabe no meio da mão."""
        if not self._fixo and len(self._cartas) < minimo:
            self._reabastecer()

    def comprar(self):
        if not self._cartas:
            raise ValueError("O baralho acabou")
        return self._cartas.popleft()


class Mao:
    """Cartas de um participante. Calcula o melhor total considerando o Ás."""

    def __init__(self):
        self.cartas = []

    def adicionar(self, carta):
        self.cartas.append(carta)

    def limpar(self):
        self.cartas = []

    @property
    def valor(self):
        total = sum(c.pontos for c in self.cartas)
        ases = sum(1 for c in self.cartas if c.valor == "A")
        # Cada Ás pode valer 1 em vez de 11 para evitar estourar
        while total > 21 and ases:
            total -= 10
            ases -= 1
        return total

    @property
    def macia(self):
        """Mão 'soft': tem um Ás ainda contando como 11."""
        duro = sum(1 if c.valor == "A" else c.pontos for c in self.cartas)
        return any(c.valor == "A" for c in self.cartas) and duro + 10 <= 21

    @property
    def estourou(self):
        return self.valor > 21

    @property
    def blackjack(self):
        return len(self.cartas) == 2 and self.valor == 21


class MesaBlackjack:
    """Orquestra uma rodada: saldo, aposta, jogadas e liquidação.

    O jogo do dealer é feito passo a passo (`dealer_passo`) para a
    interface poder animar uma carta de cada vez.
    """

    def __init__(self, saldo_inicial=1000, baralho=None):
        self.saldo = saldo_inicial
        self.baralho = baralho or Baralho()
        self.jogador = Mao()
        self.dealer = Mao()
        self.aposta = 0
        self.fase = APOSTANDO
        self.dealer_revelada = False
        # Preenchidos quando a rodada termina
        self.resultado = None   # "blackjack" | "vitoria" | "empate" | "derrota"
        self.liquido = 0        # ganho líquido da rodada (negativo = perdeu)

    # ---------- consultas ----------
    @property
    def pode_dobrar(self):
        return (
            self.fase == JOGADOR
            and len(self.jogador.cartas) == 2
            and self.saldo >= self.aposta * 2
        )

    # ---------- ações do jogador ----------
    def apostar(self, valor):
        """Faz a aposta e distribui as cartas iniciais."""
        if self.fase != APOSTANDO:
            raise ValueError("Já existe uma rodada em andamento")
        if valor <= 0 or valor > self.saldo:
            raise ValueError("Valor inválido ou saldo insuficiente")

        self.aposta = valor
        self.baralho.reembaralhar_se_preciso()
        self.dealer_revelada = False
        self.resultado = None
        self.liquido = 0

        # Ordem real da mesa: jogador, dealer, jogador, dealer
        self.jogador.adicionar(self.baralho.comprar())
        self.dealer.adicionar(self.baralho.comprar())
        self.jogador.adicionar(self.baralho.comprar())
        self.dealer.adicionar(self.baralho.comprar())

        # Blackjack natural de qualquer lado encerra a rodada na hora
        if self.jogador.blackjack or self.dealer.blackjack:
            self._finalizar()
        else:
            self.fase = JOGADOR

    def pedir(self):
        if self.fase != JOGADOR:
            raise ValueError("Não é a vez do jogador")
        self.jogador.adicionar(self.baralho.comprar())
        if self.jogador.estourou:
            self._finalizar()
        elif self.jogador.valor == 21:
            self.parar()  # com 21 não há o que fazer, passa a vez

    def parar(self):
        if self.fase != JOGADOR:
            raise ValueError("Não é a vez do jogador")
        self.fase = DEALER
        self.dealer_revelada = True

    def dobrar(self):
        """Dobra a aposta, recebe exatamente 1 carta e para."""
        if not self.pode_dobrar:
            raise ValueError("Não é possível dobrar agora")
        self.aposta *= 2
        self.jogador.adicionar(self.baralho.comprar())
        if self.jogador.estourou:
            self._finalizar()
        else:
            self.parar()

    # ---------- dealer ----------
    def dealer_passo(self):
        """Um passo do dealer. Retorna True se comprou carta, False se terminou."""
        if self.fase != DEALER:
            raise ValueError("Não é a vez do dealer")
        if self.dealer.valor < 17:
            self.dealer.adicionar(self.baralho.comprar())
            return True
        self._finalizar()
        return False

    def dealer_jogar(self):
        """Joga a vez do dealer inteira de uma vez (útil em testes)."""
        while self.fase == DEALER:
            self.dealer_passo()

    # ---------- fim de rodada ----------
    def _finalizar(self):
        j, d = self.jogador, self.dealer
        self.dealer_revelada = True

        if j.estourou:
            self.resultado, self.liquido = "derrota", -self.aposta
        elif j.blackjack and d.blackjack:
            self.resultado, self.liquido = "empate", 0
        elif j.blackjack:
            self.resultado, self.liquido = "blackjack", self.aposta * 3 // 2
        elif d.blackjack:
            self.resultado, self.liquido = "derrota", -self.aposta
        elif d.estourou or j.valor > d.valor:
            self.resultado, self.liquido = "vitoria", self.aposta
        elif j.valor < d.valor:
            self.resultado, self.liquido = "derrota", -self.aposta
        else:
            self.resultado, self.liquido = "empate", 0

        self.saldo += self.liquido
        self.fase = FIM

    def nova_rodada(self):
        """Limpa a mesa para a próxima aposta."""
        if self.fase != FIM:
            raise ValueError("A rodada ainda não terminou")
        self.jogador.limpar()
        self.dealer.limpar()
        self.aposta = 0
        self.dealer_revelada = False
        self.fase = APOSTANDO

    def reiniciar(self, saldo_inicial=1000):
        """Recomeça do zero (usado quando o saldo acaba)."""
        self.saldo = saldo_inicial
        self.jogador.limpar()
        self.dealer.limpar()
        self.aposta = 0
        self.dealer_revelada = False
        self.resultado = None
        self.liquido = 0
        self.fase = APOSTANDO