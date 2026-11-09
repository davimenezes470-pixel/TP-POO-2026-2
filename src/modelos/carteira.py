class Carteira:
    def __init__(self, saldo_inicial):
        self.saldo_inicial = saldo_inicial
        self.saldo = saldo_inicial

    @property
    def falido(self):
        return self.saldo <= 0

    def reiniciar(self):
        self.saldo = self.saldo_inicial