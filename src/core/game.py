import ctypes
import random
import sys
import pygame
from core.state_manager import StateManager
import config


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass


class Game:

    def __init__(self):
        pygame.init()

        # Dimensões padrão para o modo janela
        self.window_width = config.SCREEN_WIDTH
        self.window_height = config.SCREEN_HEIGHT

        self.is_fullscreen = False

        # Cria a janela inicial
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(config.TITLE)

        self.clock = pygame.time.Clock()
        self.running = True


    def toggle_fullscreen(self):
        """Alterna dinamicamente o modo de exibição da tela."""
        self.is_fullscreen = not self.is_fullscreen

        if self.is_fullscreen:
            # Alterna para Tela Cheia usando a resolução nativa do monitor
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # Retorna para o modo Janela com o tamanho definido
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # Trata a tecla F11
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()

                # Tecla ESC para sair da tela cheia ou fechar o jogo
                elif event.key == pygame.K_ESCAPE:
                    if self.is_fullscreen:
                        self.toggle_fullscreen()
                    else:
                        self.running = False

    def run(self):
        while self.running:
            self.process_events()
            self.clock.tick(config.FPS)

        pygame.quit()
        sys.exit()