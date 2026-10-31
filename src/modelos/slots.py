import random

# Fita de cada rolo. Repetir um símbolo = aumentar a chance dele aparecer.
# (7 cerejas, 5 limões, 4 sinos, 2 tigres, 2 setes = 20 posições)
FITA = (
    "cereja", "limao", "sino", "cereja", "sete", "limao", "cereja", "tigre", "sino", "cereja",
    "limao", "cereja", "sino", "limao", "tigre", "cereja", "limao", "sete", "cereja", "sino",
)
# Lucro por unidade apostada na linha quando saem 3 símbolos iguais (ex.: 8 = 8:1).
PAGAMENTO = {"cereja": 8, "limao": 10, "sino": 20, "sete": 100, "tigre": 150}

# Linhas de pagamento: a linha (0=topo, 1=meio, 2=base) usada em cada um dos 3 rolos.
LINHAS = ((1, 1, 1), (0, 0, 0), (2, 2, 2), (0, 1, 2), (2, 1, 0))

NUM_ROLOS = 3
NUM_LINHAS = 3

class Vitoria:

    def __init__(self, linha, simbolo, premio):
        self.linha = linha      # índice em LINHAS
        self.simbolo = simbolo
        self.premio = premio

    def __repr__(self):
        return f"Vitoria(linha={self.linha}, {self.simbolo}, premio={self.premio})"

class ResultadoGiro:

    def __init__(self, paradas, grade, vitorias=None):
        self.paradas = paradas                # posição de parada de cada rolo na fita
        self.grade = grade                    # grade[rolo][linha] -> símbolo visível
        self.vitorias = vitorias or []
        self.premio = sum(v.premio for v in self.vitorias)  # bruto, sem descontar a aposta

class Rolos:

    def __init__(self, rng=None, fita=FITA):
        self.fita = tuple(fita)
        # rng injetável: permite fixar a semente nos testes
        self._rng = rng or random.Random()

    def sortear_paradas(self):
        return [self._rng.randrange(len(self.fita)) for _ in range(NUM_ROLOS)]

    def visiveis(self, parada):

        n = len(self.fita)
        return [self.fita[(parada - 1 + r) % n] for r in range(NUM_LINHAS)]

    def parada_do_simbolo(self, simbolo):
        for i, s in enumerate(self.fita):
            if s == simbolo:
                return i
        raise ValueError(f"Símbolo inválido: {simbolo}")

def calcular_vitorias(grade, valor):

    vitorias = []
    for i, linha in enumerate(LINHAS):
        simbolos = [grade[rolo][row] for rolo, row in enumerate(linha)]
        if len(set(simbolos)) == 1:
            vitorias.append(Vitoria(i, simbolos[0], PAGAMENTO[simbolos[0]] * valor))
    return vitorias

class MesaSlots:

    def __init__(self, saldo_inicial=1000, rolos=None):
        self.saldo = saldo_inicial
        self.rolos = rolos or Rolos()
        self.aposta = 0        
        self.resultado = None  

    @property
    def custo(self):
        return self.aposta * len(LINHAS)

    @staticmethod
    def custo_de(valor):
        return valor * len(LINHAS)

    def apostar(self, valor):
        if self.aposta:
            raise ValueError("Já existe uma aposta em andamento")
        if valor <= 0 or self.custo_de(valor) > self.saldo:
            raise ValueError("Valor inválido ou saldo insuficiente")
        self.aposta = valor
        self.resultado = None

    def sortear(self, paradas_forcadas=None):

        if not self.aposta:
            raise ValueError("Faça uma aposta antes de girar")
        paradas = list(paradas_forcadas) if paradas_forcadas is not None else self.rolos.sortear_paradas()
        grade = [self.rolos.visiveis(p) for p in paradas]
        vitorias = calcular_vitorias(grade, self.aposta)
        self.resultado = ResultadoGiro(paradas, grade, vitorias)
        return self.resultado

    def liquidar(self):

        if self.resultado is None or not self.aposta:
            raise ValueError("Não há rodada para liquidar")
        liquido = self.resultado.premio - self.custo
        self.saldo += liquido
        self.aposta = 0
        return liquido

    def reiniciar(self, saldo_inicial=1000):

        self.saldo = saldo_inicial
        self.aposta = 0
        self.resultado = None

def simular_rtp(giros=500_000, rng=None):
  
    rolos = Rolos(rng)
    apostado = pago = 0
    for _ in range(giros):
        grade = [rolos.visiveis(p) for p in rolos.sortear_paradas()]
        apostado += len(LINHAS)
        pago += sum(v.premio for v in calcular_vitorias(grade, 1))
    return pago / apostado

if __name__ == "__main__":
    print(f"RTP simulado: {simular_rtp():.2%}")
