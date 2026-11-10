#Módulo responsável pelo gerenciamento financeiro do jogador.
class Carteira:
    #Representa a carteira do jogador, controlando saldo e notificações ao tracker.
    def __init__(self, saldo_inicial, tracker=None):
        #Inicializa a carteira com o saldo inicial e referência opcional ao tracker.
        self.saldo_inicial = saldo_inicial
        self.tracker = tracker
        self._saldo = saldo_inicial  # Usamos _saldo internamente

    @property
    def saldo(self):
        #Retorna o saldo atual disponível na carteira.
        return self._saldo

    @saldo.setter
    def saldo(self, novo_valor):
        #Atualiza o saldo e registra a diferença financeira no tracker.
        diferenca = novo_valor - self._saldo
        if self.tracker and diferenca != 0:
            self.tracker.registrar_dinheiro(diferenca)
        
        self._saldo = novo_valor

    @property
    def falido(self):
        #Indica se o saldo atual está zerado ou negativo.
        return self._saldo <= 0

    def reiniciar(self):
        #Restaura o saldo para o valor inicial sem contabilizar ganho no histórico.
        self._saldo = self.saldo_inicial