import ctypes
import random
import sys
import os #centraliza a janela automaticamente, se ajustando ao monitor
import pygame
from core.state_manager import StateManager
from states.menu_state import MenuState
from states.game_state import GameState
from states.roleta_state import RoletaState
from states.black_state import BlackjackState
from states.celular_state import CelularState
from states.casaFora_state import CasaForaState
from states.noite_state import NoiteState
import config
from modelos.player import Player
from states.cutscene_state import CutsceneState
from states.slots_state import SlotsState
from states.gameover_state import GameOverState
from core.tracker import Tracker
from states.runs_state import RunsState


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'

class Game:

    def __init__(self):
        pygame.init()

        # Dimensões padrão para o modo janela
        self.window_width = config.SCREEN_WIDTH
        self.window_height = config.SCREEN_HEIGHT

        self.is_fullscreen = False

        # Cria a janela inicial
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
        pygame.display.set_caption(config.TITLE)

        screen_max = pygame.display.get_wm_info().get('window')
        if screen_max:
            try:
                ctypes.windll.user32.ShowWindow(screen_max, 3)
            except Exception:
                pass

        self.tracker = Tracker()                
        self.tracker.adicionar_run()

        self.player = Player(100, 720-512, self.tracker)

        self.clock = pygame.time.Clock()
        self.running = True

        self.game_over_timer = None
        self._criar_estados()

    def _criar_estados(self):
        self.state_manager = StateManager()
        cenas_intro = [
            {
                "imagem": 'assets/casacutscene.png',
                "texto": "AGIOTA: Essa é a ultima vez que te empresto dinheiro!!"
            },
            {
                "imagem": 'assets/casacutscene.png', 
                "texto": "AGIOTA: Vou levar esse carro como garantia do meu pagamento"
            }
        ]
        self.state_manager.add_state("Intro", CutsceneState(self, self.state_manager, cenas_intro, "CasaFora"))
        self.state_manager.add_state("Menu", MenuState(self, self.state_manager))
        self.state_manager.add_state("Jogo", GameState(self, self.state_manager))
        self.state_manager.add_state("Celular", CelularState(self, self.state_manager))
        self.state_manager.add_state("Roleta", RoletaState(self, self.state_manager))
        self.state_manager.add_state("Blackjack", BlackjackState(self, self.state_manager))
        self.state_manager.add_state("Tigrinho", SlotsState(self, self.state_manager))
        self.state_manager.add_state("GameOver", GameOverState(self, self.state_manager))
        self.state_manager.add_state("Noite", NoiteState(self, self.state_manager))
        self.state_manager.add_state("CasaFora", CasaForaState(self, self.state_manager))
        self.state_manager.add_state("Runs", RunsState(self, self.state_manager))
        self.state_manager.change_state("Menu")

    def agendar_game_over(self, atraso=2.0):
        if self.game_over_timer is None:
            self.game_over_timer = atraso

    def novo_jogo(self):
        self.tracker.adicionar_run()
        self.player.carteira.reiniciar()
        self.game_over_timer = None
        self._criar_estados()


    def toggle_fullscreen(self):
        """Alterna dinamicamente o modo de exibição da tela."""
        self.is_fullscreen = not self.is_fullscreen

        if self.is_fullscreen:
            # Alterna para Tela Cheia usando a resolução nativa do monitor
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # Retorna para o modo Janela com o tamanho definido
            self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE | pygame.WINDOWMAXIMIZED)

    def process_events(self):

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # Trata a tecla F11
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()

        self.state_manager.process_events(events)

    def run(self):
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0

            self.process_events()
            self.state_manager.update(dt)

            if self.game_over_timer is not None:
                self.game_over_timer -= dt
                if self.game_over_timer <= 0:
                    self.game_over_timer = None
                    self.state_manager.change_state("GameOver")

            self.screen.fill(getattr(config, 'COLOR_BG', (24, 24, 28)))
            self.state_manager.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()
