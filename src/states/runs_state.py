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
        self.pagina_atual = 0  

    def process_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Volta de onde veio
                    origem = getattr(self.game, 'origem_runs', 'Menu')
                    self.state_manager.change_state(origem)
                
                # Navegação nas páginas
                elif event.key == pygame.K_RIGHT:
                    total_runs = len(self.game.tracker.dados["runs"])
                    if total_runs > 0:
                        self.pagina_atual = (self.pagina_atual + 1) % total_runs
                elif event.key == pygame.K_LEFT:
                    total_runs = len(self.game.tracker.dados["runs"])
                    if total_runs > 0:
                        self.pagina_atual = (self.pagina_atual - 1) % total_runs

    def update(self, dt):
        pass

    def draw(self, surface):
        w, h = surface.get_size()
        surface.fill((20, 20, 24))  

        runs = self.game.tracker.dados["runs"]

        if not runs:
            txt = self.fonte_texto.render("Nenhuma run registrada.", True, config.COLOR_WHITE)
            surface.blit(txt, txt.get_rect(center=(w // 2, h // 2)))
        else:
            # Garante que o índice não quebre se o arquivo for resetado
            if self.pagina_atual >= len(runs):
                self.pagina_atual = len(runs) - 1
                
            run = runs[self.pagina_atual]
            
            # Textos a serem exibidos
            textos = [
                (self.fonte_titulo, f"RUN #{run['numero']}", config.COLOR_WHITE, -160),
                (self.fonte_texto, f"Dinheiro Ganho: R$ {run['ganhos']:,}", (100, 220, 120), -80),
                (self.fonte_texto, f"Dinheiro Perdido: R$ {run['perdas']:,}", (220, 100, 100), -30),
                (self.fonte_texto, "--- Quantidade de Jogadas ---", (180, 180, 180), 30),
                (self.fonte_texto, f"Roleta: {run['jogos']['Roleta']}", config.COLOR_WHITE, 80),
                (self.fonte_texto, f"Blackjack: {run['jogos']['Blackjack']}", config.COLOR_WHITE, 120),
                (self.fonte_texto, f"Tigrinho: {run['jogos']['Tigrinho']}", config.COLOR_WHITE, 160)
            ]

            for fonte, texto, cor, offset_y in textos:
                surf = fonte.render(texto, True, cor)
                rect = surf.get_rect(center=(w // 2, h // 2 + offset_y))
                surface.blit(surf, rect)
            
            # Guia de Paginação inferior
            paginacao = self.fonte_dica.render(f"Página {self.pagina_atual + 1} de {len(runs)} (Use as setas <- ->)", True, (150, 150, 150))
            surface.blit(paginacao, paginacao.get_rect(center=(w // 2, h // 2 + 220)))

        # Dica de voltar
        dica = self.fonte_dica.render("Pressione ESC para voltar", True, (150, 150, 150))
        surface.blit(dica, dica.get_rect(center=(w // 2, h - 50)))