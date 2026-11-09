import pygame
from states.base_state import BaseState

class GameOverState(BaseState):
    def __init__(self, game, state_manager):
        super().__init__(state_manager)
        self.game = game
        self.fonte_big = pygame.font.Font(None, 120)
        self.fonte = pygame.font.Font(None, 40)

    def process_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game.novo_jogo()
                elif event.key == pygame.K_ESCAPE:
                    self.game.running = False

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((10, 10, 12))
        w, h = surface.get_size()
        titulo = self.fonte_big.render("GAME OVER", True, (200, 30, 40))
        sub = self.fonte.render("Você perdeu tudo.  ENTER: recomeçar   ESC: sair", True, (220, 220, 220))
        surface.blit(titulo, titulo.get_rect(center=(w // 2, h // 2 - 40)))
        surface.blit(sub, sub.get_rect(center=(w // 2, h // 2 + 50)))