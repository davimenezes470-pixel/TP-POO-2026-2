import json
import os

# Salva o arquivo na raiz do projeto
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAMINHO_ARQUIVO = os.path.join(RAIZ, "runs_data.json")

class Tracker:
    def __init__(self):
        self.dados = {"runs": 0, "ganhos": 0, "perdas": 0}
        self.carregar()

    def carregar(self):
        """Lê o arquivo se ele existir."""
        if os.path.exists(CAMINHO_ARQUIVO):
            try:
                with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
                    self.dados = json.load(f)
            except:
                pass

    def salvar(self):
        """Salva as informações no HD."""
        with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, indent=4)

    def adicionar_run(self):
        """Adiciona +1 ao total de runs jogadas."""
        self.dados["runs"] += 1
        self.salvar()

    def registrar_dinheiro(self, diferenca):
        """Avalia se o dinheiro foi ganho ou perdido e soma no histórico."""
        if diferenca > 0:
            self.dados["ganhos"] += diferenca
        elif diferenca < 0:
            # Guardamos o valor positivo da perda
            self.dados["perdas"] += abs(diferenca)
        self.salvar()