import json
import os

# Salva o arquivo na raiz do projeto
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAMINHO_ARQUIVO = os.path.join(RAIZ, "runs_data.json")

class Tracker:
    def __init__(self):
        self.dados = {"runs": []}
        self.carregar()

    def carregar(self):
        """Lê o arquivo se ele existir."""
        if os.path.exists(CAMINHO_ARQUIVO):
            try:
                with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
                    dados_salvos = json.load(f)
                    if "runs" in dados_salvos and isinstance(dados_salvos["runs"], list):
                        self.dados = dados_salvos
                    else:
                        self.dados = {"runs": []}
            except:
                pass

    def salvar(self):
        """Salva as informações no HD."""
        with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, indent=4)

    def adicionar_run(self):
        """Cria uma nova run no histórico."""
        numero_nova_run = len(self.dados["runs"]) + 1
        nova_run = {
            "numero": numero_nova_run,
            "ganhos": 0,
            "perdas": 0,
            "dias_jogados": 1,
            "jogos": {
                "Roleta": 0,
                "Blackjack": 0,
                "Tigrinho": 0
            }
        }
        self.dados["runs"].append(nova_run)
        self.dia_atual = 1
        self.apostas_hoje = 0
        self.salvar()

    def registrar_dinheiro(self, diferenca):
        """Adiciona ganhos ou perdas na run atual (a última da lista)."""
        if not self.dados["runs"]:
            return
            
        run_atual = self.dados["runs"][-1]
        
        if diferenca > 0:
            run_atual["ganhos"] += diferenca
        elif diferenca < 0:
            run_atual["perdas"] += abs(diferenca)
        self.salvar()
    def registrar_jogada(self, nome_jogo):
        """Registra que um jogo foi jogado na run atual."""
        if not self.dados["runs"]:
            return
            
        run_atual = self.dados["runs"][-1]
        if nome_jogo in run_atual["jogos"]:
            run_atual["jogos"][nome_jogo] += 1
        self.apostas_hoje += 1
        self.salvar()
    def avancar_dia(self):
        """Método novo chamado pela cutscene da noite."""
        self.dia_atual += 1
        self.apostas_hoje = 0
        if self.dados["runs"]:
            self.dados["runs"][-1]["dias_jogados"] = self.dia_atual
        self.salvar()