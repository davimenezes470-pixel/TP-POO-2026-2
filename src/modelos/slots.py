#Módulo com a lógica matemática e regras do minigame Caça-Níquel (Tigrinho).
import random
# (8 cerejas, 6 limões, 3 sacos, 2 setes, 1 tigre = 20 posições)
FITA = (
    "cereja", "limao", "cereja", "saco", "limao", "cereja", "sete", "cereja", "limao", "cereja",
    "tigre", "limao", "cereja", "saco", "limao", "cereja", "sete", "cereja", "limao", "saco",
)
CORINGA = "tigre"
PAGAMENTO = {"cereja": 5, "limao": 6, "saco": 10, "sete": 30, "tigre": 180}

LINHAS = ((1, 1, 1), (0, 0, 0), (2, 2, 2), (0, 1, 2), (2, 1, 0))

NUM_ROLOS = 3
NUM_LINHAS = 3

class Vitoria:
    #Representa uma linha premiada em uma rodada do caça-níquel.
    def __init__(self, linha, simbolo, premio):
        #Inicializa o registro de vitória de uma linha.
        self.linha = linha      
        self.simbolo = simbolo
        self.premio = premio

    def __repr__(self):
        return f"Vitoria(linha={self.linha}, {self.simbolo}, premio={self.premio})"

class ResultadoGiro:
    #Agrupa as posições sorteadas, a grade resultante e as vitórias de um giro.
    def __init__(self, paradas, grade, vitorias=None):
        #Inicializa o resultado completo de um giro.
        self.paradas = paradas                
        self.grade = grade                    
        self.vitorias = vitorias or []
        self.premio = sum(v.premio for v in self.vitorias)  

class Rolos:
    #Gerencia a fita de símbolos e o sorteio das posições dos rolos.
    def __init__(self, rng=None, fita=FITA):
        #Inicializa os rolos com uma fita e um gerador aleatório.
        self.fita = tuple(fita)
        self._rng = rng or random.Random()

    def sortear_paradas(self):
        #Sorteia uma posição aleatória da fita para cada um dos rolos.
        return [self._rng.randrange(len(self.fita)) for _ in range(NUM_ROLOS)]

    def visiveis(self, parada):
        #Retorna os 3 símbolos visíveis na vertical a partir da posição de parada.
        n = len(self.fita)
        return [self.fita[(parada - 1 + r) % n] for r in range(NUM_LINHAS)]

    def parada_do_simbolo(self, simbolo):
        #Retorna o primeiro índice da fita que contém o símbolo informado.
        for i, s in enumerate(self.fita):
            if s == simbolo:
                return i
        raise ValueError(f"Símbolo inválido: {simbolo}")

def simbolo_da_linha(simbolos):
    #Determina o símbolo vencedor de uma linha considerando o tigre como coringa.
    comuns = {s for s in simbolos if s != CORINGA}
    if not comuns:
        return CORINGA
    if len(comuns) == 1:
        return next(iter(comuns))
    return None

def calcular_vitorias(grade, valor):
    #Avalia todas as linhas de pagamento da grade e retorna a lista de vitórias.
    vitorias = []
    for i, linha in enumerate(LINHAS):
        simbolos = [grade[rolo][row] for rolo, row in enumerate(linha)]
        simbolo = simbolo_da_linha(simbolos)
        if simbolo:
            vitorias.append(Vitoria(i, simbolo, PAGAMENTO[simbolo] * valor))
    return vitorias

class MesaSlots:
    #Orquestra uma rodada de caça-níquel: aposta, sorteio e liquidação.
    def __init__(self, carteira, rolos=None):
        #Inicializa a mesa associada à carteira do jogador.
        self.carteira = carteira
        self.rolos = rolos or Rolos()
        self.aposta = 0        
        self.resultado = None 

    @property
    def saldo(self):
        #Retorna o saldo disponível na carteira.
        return self.carteira.saldo

    @saldo.setter
    def saldo(self, valor):
        #Atualiza o saldo na carteira.
        self.carteira.saldo = valor

    @property
    def custo(self):
        #Retorna o custo total da rodada atual (aposta multiplicada pelo número de linhas).
        return self.aposta * len(LINHAS)

    @staticmethod
    def custo_de(valor):
        #Calcula o custo total de uma rodada para um dado valor por linha.
        return valor * len(LINHAS)

    def apostar(self, valor):
        #Valida e registra a aposta por linha antes do giro.
        if self.aposta:
            raise ValueError("Já existe uma aposta em andamento")
        if valor <= 0 or self.custo_de(valor) > self.saldo:
            raise ValueError("Valor inválido ou saldo insuficiente")
        self.aposta = valor
        self.resultado = None

    def sortear(self, paradas_forcadas=None, grade_forcada=None):
        #Executa o sorteio dos rolos e calcula as linhas vencedoras.
        if not self.aposta:
            raise ValueError("Faça uma aposta antes de girar")
        paradas = list(paradas_forcadas) if paradas_forcadas is not None else self.rolos.sortear_paradas()
        if grade_forcada is not None:
            grade = [list(coluna) for coluna in grade_forcada]
        else:
            grade = [self.rolos.visiveis(p) for p in paradas]
        vitorias = calcular_vitorias(grade, self.aposta)
        self.resultado = ResultadoGiro(paradas, grade, vitorias)
        return self.resultado

    def liquidar(self):
        #Aplica o ganho ou perda líquida ao saldo e encerra a rodada.
        if self.resultado is None or not self.aposta:
            raise ValueError("Não há rodada para liquidar")
        liquido = self.resultado.premio - self.custo
        self.saldo += liquido
        self.aposta = 0
        return liquido

    def reiniciar(self):
        #Zera a aposta e limpa o resultado atual da mesa.
        self.aposta = 0
        self.resultado = None

#Retorno de 91% do que entra
def simular_rtp(giros=500_000, rng=None):
    #Simula milhares de giros para estimar o retorno teórico ao jogador (RTP).
    rolos = Rolos(rng)
    apostado = pago = 0
    for _ in range(giros):
        grade = [rolos.visiveis(p) for p in rolos.sortear_paradas()]
        apostado += len(LINHAS)
        pago += sum(v.premio for v in calcular_vitorias(grade, 1))
    return pago / apostado

if __name__ == "__main__":
    print(f"RTP simulado: {simular_rtp():.2%}")
