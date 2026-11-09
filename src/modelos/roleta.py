"""Lógica do jogo de roleta europeia (0-36).

Este módulo NÃO depende do pygame: assim a regra do jogo pode ser testada
isoladamente e a interface (states/roleta_state.py) só precisa consumi-la.
"""
import random
from abc import ABC, abstractmethod

# Ordem física das casas na roda europeia (sentido horário).
ORDEM_RODA = (
    0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10,
    5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26,
)
VERMELHOS = frozenset({1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36})


class Casa:
    """Uma casa da roda: número + cor (derivada do número)."""

    def __init__(self, numero):
        self.numero = numero
        if numero == 0:
            self.cor = "verde"
        elif numero in VERMELHOS:
            self.cor = "vermelho"
        else:
            self.cor = "preto"

    @property
    def par(self):
        return self.numero != 0 and self.numero % 2 == 0

    @property
    def impar(self):
        return self.numero % 2 == 1

    def __repr__(self):
        return f"Casa({self.numero}, {self.cor})"


class Roleta:
    """A roda: guarda as casas na ordem física e sorteia uma delas."""

    def __init__(self, rng=None):
        self.casas = [Casa(n) for n in ORDEM_RODA]
        # rng injetável: permite fixar a semente nos testes
        self._rng = rng or random.Random()

    def girar(self):
        return self._rng.choice(self.casas)

    def indice_de(self, casa):
        return self.casas.index(casa)

    def casa_do_numero(self, numero):
        for casa in self.casas:
            if casa.numero == numero:
                return casa
        raise ValueError("Número deve estar entre 0 e 36")


class Aposta(ABC):
    """Classe base. Cada tipo de aposta define a própria regra e o pagamento."""

    def __init__(self, valor):
        self.valor = valor

    @property
    @abstractmethod
    def descricao(self):
        """Texto exibido na interface."""

    @property
    @abstractmethod
    def pagamento(self):
        """Lucro por unidade apostada quando vence (ex.: 35 significa 35:1)."""

    @abstractmethod
    def venceu(self, casa):
        """Retorna True se a aposta ganha com a casa sorteada."""

    def resultado(self, casa):
        """Ganho líquido: +lucro se venceu, -valor se perdeu."""
        return self.valor * self.pagamento if self.venceu(casa) else -self.valor


class ApostaNumero(Aposta):
    def __init__(self, valor, numero):
        if numero not in ORDEM_RODA:
            raise ValueError("Número deve estar entre 0 e 36")
        super().__init__(valor)
        self.numero = numero

    @property
    def descricao(self):
        return f"Número {self.numero}"

    @property
    def pagamento(self):
        return 35

    def venceu(self, casa):
        return casa.numero == self.numero


class ApostaCor(Aposta):
    def __init__(self, valor, cor):
        if cor not in ("vermelho", "preto"):
            raise ValueError("Cor deve ser 'vermelho' ou 'preto'")
        super().__init__(valor)
        self.cor = cor

    @property
    def descricao(self):
        return self.cor.capitalize()

    @property
    def pagamento(self):
        return 1

    def venceu(self, casa):
        return casa.cor == self.cor  # o zero (verde) sempre perde


class ApostaParidade(Aposta):
    def __init__(self, valor, paridade):
        if paridade not in ("par", "impar"):
            raise ValueError("Paridade deve ser 'par' ou 'impar'")
        super().__init__(valor)
        self.paridade = paridade

    @property
    def descricao(self):
        return "Par" if self.paridade == "par" else "Ímpar"

    @property
    def pagamento(self):
        return 1

    def venceu(self, casa):
        return casa.par if self.paridade == "par" else casa.impar


class MesaRoleta:
    """Orquestra uma rodada: saldo, aposta atual, sorteio e liquidação.

    O sorteio e a liquidação são separados para a interface poder animar
    a roda antes de mostrar o novo saldo.
    """

    def __init__(self, carteira, roleta=None):
        self.carteira = carteira
        self.roleta = roleta or Roleta()
        self.aposta = None
        self.casa_sorteada = None
    @property
    def saldo(self):
        return self.carteira.saldo

    @saldo.setter
    def saldo(self, valor):
        self.carteira.saldo = valor

    def apostar(self, aposta):
        if self.aposta is not None:
            raise ValueError("Já existe uma aposta em andamento")
        if aposta.valor <= 0 or aposta.valor > self.saldo:
            raise ValueError("Valor inválido ou saldo insuficiente")
        self.aposta = aposta

    def sortear(self, numero_forcado=None):
        """Sorteia a casa. Se numero_forcado for dado (modo teste), ignora o acaso."""
        if self.aposta is None:
            raise ValueError("Faça uma aposta antes de girar")
        if numero_forcado is None:
            self.casa_sorteada = self.roleta.girar()
        else:
            self.casa_sorteada = self.roleta.casa_do_numero(numero_forcado)
        return self.casa_sorteada

    def liquidar(self):
        """Aplica o resultado ao saldo e encerra a rodada. Retorna o ganho líquido."""
        liquido = self.aposta.resultado(self.casa_sorteada)
        self.saldo += liquido
        self.aposta = None
        return liquido
