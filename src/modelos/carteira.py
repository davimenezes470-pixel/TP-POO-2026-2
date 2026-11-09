class Carteira:
    def __init__(self, saldo_inicial, tracker=None):
        self.saldo_inicial = saldo_inicial
        self.tracker = tracker
        self._saldo = saldo_inicial  # Usamos _saldo internamente

    @property
    def saldo(self):
        return self._saldo

    @saldo.setter
    def saldo(self, novo_valor):
        diferenca = novo_valor - self._saldo
        # Se houver um tracker e o dinheiro mudou, registra a diferença
        if self.tracker and diferenca != 0:
            self.tracker.registrar_dinheiro(diferenca)
        
        self._saldo = novo_valor

    @property
    def falido(self):
        return self._saldo <= 0

    def reiniciar(self):
        # Acessamos _saldo diretamente para que o recomeço do jogo 
        # não conte como "ganho" no histórico.
        self._saldo = self.saldo_inicial