# config.py
from pathlib import Path

# --- CAMINHOS ---
RAIZ = Path(__file__).resolve().parent.parent
PASTA_ASSETS = RAIZ / "assets"
ARQUIVO_RUNS = RAIZ / "runs_data.json"

# --- CONFIGURAÇÕES DA TELA ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Demo: Tigrinho - RPG & Minigames"
NAME_PHONE = "Apple: Iphone 18 Pro Max"

# --- CORES (RGB) ---
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

# --- A PARTE ---
COLOR_BG = (24, 24, 28)
SALDO_INICIAL = 5000

# --- FÍSICA E JOGABILIDADE ---
# --- EXEMPLOS ---
PLAYER_SPEED = 5
TILE_SIZE = 40