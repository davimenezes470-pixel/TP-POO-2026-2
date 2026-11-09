import pygame
import config
from states.base_state import BaseState


class MenuState(BaseState):

    def __init__(self, game, state_manager):
        super().__init__(state_manager)
        self.game = game
        self.options = ["Jogar", "Historico de runs", "Sair"]
        self.selected_index = 0

        self.font_title = pygame.font.Font(None, 52)
        self.font_options = pygame.font.Font(None, 36)

    def process_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    self.state_manager.change_state("Jogo")
                elif event.key in (pygame.K_3, pygame.K_KP2):
                    self.state_manager.change_state("Runs")
                elif event.key in (pygame.K_4, pygame.K_KP3):
                    self.game.running = False

                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_index = (self.selected_index + 1) % len(self.options)

                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._select_option()

    def _select_option(self):
        if self.selected_index == 0:
            self.state_manager.change_state("Aviso")
        elif self.selected_index == 1:
            self.game.origem_runs = "Menu"
            self.state_manager.change_state("Runs")
        elif self.selected_index == 2:
            self.game.running = False

    def update(self, dt):
        pass

    def draw(self, surface):
        w, h = surface.get_size()

        title_surf = self.font_title.render(config.TITLE, True, config.COLOR_WHITE)
        title_rect = title_surf.get_rect(center=(w // 2, 160))
        surface.blit(title_surf, title_rect)

        for idx, option in enumerate(self.options):
            is_selected = idx == self.selected_index
            color = (255, 0, 0) if is_selected else config.COLOR_WHITE
            label = f"> {option} <" if is_selected else f" {option}"

            surf = self.font_options.render(label, True, color)
            rect = surf.get_rect(center=(w // 2, 300 + (idx * 60)))
            surface.blit(surf, rect)
