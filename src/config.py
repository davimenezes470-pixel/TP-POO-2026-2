#Módulo de configurações globais, caminhos de arquivos e constantes do jogo.
import sys
from pathlib import Path

# --- CAMINHOS ---
if getattr(sys, "frozen", False):
    RAIZ = Path(sys._MEIPASS)
    PASTA_DADOS = Path(sys.executable).resolve().parent
else:
    RAIZ = Path(__file__).resolve().parent.parent
    PASTA_DADOS = RAIZ

PASTA_ASSETS = RAIZ / "assets"
ARQUIVO_RUNS = PASTA_DADOS / "runs_data.json"

# --- CONFIGURAÇÕES DA TELA ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Tigrinho Simulator"
NAME_PHONE = "Apple: Iphone 18 Pro Max"

# --- CORES (RGB) ---
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

# --- A PARTE ---
COLOR_BG = (24, 24, 28)
SALDO_INICIAL = 5000

# --- FÍSICA E JOGABILIDADE ---
PLAYER_SPEED = 5
TILE_SIZE = 40