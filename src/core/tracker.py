#Módulo de persistência de dados e rastreamento estatístico das partidas (runs).

import copy
import json
import config

# Salva o arquivo na raiz do projeto
CAMINHO_ARQUIVO = config.ARQUIVO_RUNS


class Tracker:
    #Registra e persiste em JSON o histórico de runs, ganhos, perdas e dias jogados. 

    def __init__(self):
        #Inicializa a estrutura de dados e carrega o histórico salvo em disco.
        self._dados = {"runs": []}
        self._dia_atual = 1
        self._apostas_hoje = 0
        self._dias_sem_apostar = 0
        self._carregar()

    @property
    def dia_atual(self):
        #Retorna o dia corrente da run ativa.
        return self._dia_atual

    @property
    def apostas_hoje(self):
        #Retorna o número de apostas realizadas no dia atual.
        return self._apostas_hoje

    @property
    def dias_sem_apostar(self):
        #Retorna a contagem de dias consecutivos sem realizar apostas.
        return self._dias_sem_apostar

    @property
    def total_runs(self):
        #Retorna a quantidade total de runs registradas no histórico.
        return len(self._dados["runs"])

    def obter_run(self, indice):
        #Retorna uma cópia segura dos dados da run no índice especificado. 
        if 0 <= indice < len(self._dados["runs"]):
            return copy.deepcopy(self._dados["runs"][indice])
        raise IndexError("Índice de run inválido.")

    def _carregar(self):
        #Lê o arquivo JSON de histórico caso exista no disco.
        if CAMINHO_ARQUIVO.exists():
            try:
                with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
                    dados_salvos = json.load(f)
                    if "runs" in dados_salvos and isinstance(dados_salvos["runs"], list):
                        self._dados = dados_salvos
                    else:
                        self._dados = {"runs": []}
            except Exception:
                pass

    def _salvar(self):
        #Salva as informações atuais no arquivo JSON em disco.
        with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(self._dados, f, indent=4)

    def adicionar_run(self):
        #Cria uma nova run no histórico e zera os contadores diários.
        numero_nova_run = len(self._dados["runs"]) + 1
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
        self._dados["runs"].append(nova_run)
        self._dia_atual = 1
        self._apostas_hoje = 0
        self._dias_sem_apostar = 0
        self._salvar()

    def registrar_dinheiro(self, diferenca):
        #Adiciona ganhos ou perdas na run atual (a última da lista).
        if not self._dados["runs"]:
            return

        run_atual = self._dados["runs"][-1]

        if diferenca > 0:
            run_atual["ganhos"] += diferenca
        elif diferenca < 0:
            run_atual["perdas"] += abs(diferenca)
        self._salvar()

    def registrar_jogada(self, nome_jogo):
        #Registra que um jogo foi jogado na run atual.
        if not self._dados["runs"]:
            return

        run_atual = self._dados["runs"][-1]
        if nome_jogo in run_atual["jogos"]:
            run_atual["jogos"][nome_jogo] += 1
        self._apostas_hoje += 1
        self._salvar()

    def avancar_dia(self):
        #Avança o dia atual, atualiza dias sem apostar e salva no histórico.
        if self._apostas_hoje == 0:
            self._dias_sem_apostar += 1
        else:
            self._dias_sem_apostar = 0
        self._dia_atual += 1
        self._apostas_hoje = 0
        if self._dados["runs"]:
            self._dados["runs"][-1]["dias_jogados"] = self._dia_atual
        self._salvar()