import random
# Fita de cada rolo. Repetir um símbolo = aumentar a chance dele aparecer.
# (8 cerejas, 6 limões, 3 sacos, 2 setes, 1 tigre = 20 posições)
FITA = (
    "cereja", "limao", "cereja", "saco", "limao", "cereja", "sete", "cereja", "limao", "cereja",
    "tigre", "limao", "cereja", "saco", "limao", "cereja", "sete", "cereja", "limao", "saco",
)
# O tigre é CORINGA.
CORINGA = "tigre"

# Lucro por unidade apostada na linha quando a linha completa vale esse símbolo.
PAGAMENTO = {"cereja": 5, "limao": 6, "saco": 10, "sete": 30, "tigre": 180}

LINHAS = ((1, 1, 1), (0, 0, 0), (2, 2, 2), (0, 1, 2), (2, 1, 0))

NUM_ROLOS = 3
NUM_LINHAS = 3

#qual linha, qual simbolo e quanto pagou
class Vitoria:

    def __init__(self, linha, simbolo, premio):
        self.linha = linha      
        self.simbolo = simbolo
        self.premio = premio

    def __repr__(self):
        return f"Vitoria(linha={self.linha}, {self.simbolo}, premio={self.premio})"

#premio que ganha
class ResultadoGiro:

    def __init__(self, paradas, grade, vitorias=None):
        self.paradas = paradas                
        self.grade = grade                    
        self.vitorias = vitorias or []
        self.premio = sum(v.premio for v in self.vitorias)  

#sorteiam onde cada simbolo para
class Rolos:

    def __init__(self, rng=None, fita=FITA):
        self.fita = tuple(fita)
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

def simbolo_da_linha(simbolos):

    comuns = {s for s in simbolos if s != CORINGA}
    if not comuns:
        return CORINGA
    if len(comuns) == 1:
        return next(iter(comuns))
    return None

#confere as linhas e retorna valor ganho
def calcular_vitorias(grade, valor):

    vitorias = []
    for i, linha in enumerate(LINHAS):
        simbolos = [grade[rolo][row] for rolo, row in enumerate(linha)]
        simbolo = simbolo_da_linha(simbolos)
        if simbolo:
            vitorias.append(Vitoria(i, simbolo, PAGAMENTO[simbolo] * valor))
    return vitorias

#organiza cada rodada
class MesaSlots:

    def __init__(self, carteira, rolos=None):
        self.carteira = carteira
        self.rolos = rolos or Rolos()
        self.aposta = 0        
        self.resultado = None 

    @property
    def saldo(self):
        return self.carteira.saldo

    @saldo.setter
    def saldo(self, valor):
        self.carteira.saldo = valor

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

#sorteia os rolos
    def sortear(self, paradas_forcadas=None, grade_forcada=None):

        if not self.aposta:
            raise ValueError("Faça uma aposta antes de girar")
        paradas = list(paradas_forcadas) if paradas_forcadas is not None else self.rolos.sortear_paradas()
        #J para jackpot 9 tigres
        if grade_forcada is not None:
            grade = [list(coluna) for coluna in grade_forcada]
        else:
            grade = [self.rolos.visiveis(p) for p in paradas]
        vitorias = calcular_vitorias(grade, self.aposta)
        self.resultado = ResultadoGiro(paradas, grade, vitorias)
        return self.resultado

#faz mudança no saldo de acordo com ganho ou perda
    def liquidar(self):
    
        if self.resultado is None or not self.aposta:
            raise ValueError("Não há rodada para liquidar")
        liquido = self.resultado.premio - self.custo
        self.saldo += liquido
        self.aposta = 0
        return liquido

    def reiniciar(self):

        self.aposta = 0
        self.resultado = None

#retorno de 91% do que entra
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
