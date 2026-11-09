import pygame
import config
from states.base_state import BaseState

class RunsState(BaseState):
    def __init__(self, game, state_manager):
        super().__init__(state_manager)
        self.game = game
        self.fonte_titulo = pygame.font.Font(None, 60)
        self.fonte_texto = pygame.font.Font(None, 42)
        self.fonte_dica = pygame.font.Font(None, 28)

    def process_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Descobre de onde o jogador veio (Menu ou Celular) para voltar pro lugar certo
                    origem = getattr(self.game, 'origem_runs', 'Menu')
                    self.state_manager.change_state(origem)

    def update(self, dt):
        pass

    def draw(self, surface):
        w, h = surface.get_size()
        surface.fill((20, 20, 24))  # Fundo escuro elegante

        dados = self.game.tracker.dados
        
        # Textos
        textos = [
            (self.fonte_titulo, "HISTÓRICO GERAL", config.COLOR_WHITE, -120),
            (self.fonte_texto, f"Total de Runs: {dados['runs']}", (200, 200, 200), -20),
            (self.fonte_texto, f"Dinheiro Ganho: R$ {dados['ganhos']:,}", (100, 220, 120), 40),
            (self.fonte_texto, f"Dinheiro Perdido: R$ {dados['perdas']:,}", (220, 100, 100), 100)
        ]

        for fonte, texto, cor, offset_y in textos:
            surf = fonte.render(texto, True, cor)
            rect = surf.get_rect(center=(w // 2, h // 2 + offset_y))
            surface.blit(surf, rect)

        # Dica de voltar
        dica = self.fonte_dica.render("Pressione ESC para voltar", True, (150, 150, 150))
        surface.blit(dica, dica.get_rect(center=(w // 2, h - 50)))