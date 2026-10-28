import pygame
import config
from states.base_state import BaseState

class GameState(BaseState):

    def __init__(self, game, state_manager):
        super().__init__(state_manager)
        self.game = game

    def process_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # ESC faz voltar ao menu
                if event.key == pygame.K_ESCAPE:
                    self.state_manager.change_state("Menu")

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(config.COLOR_BLACK)