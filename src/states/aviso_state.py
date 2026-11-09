import pygame
import config
from states.base_state import BaseState

class AvisoState(BaseState):
    def __init__(self, game, state_manager):
        super().__init__(state_manager)
        self.game = game
        
        self.fonte_principal = pygame.font.Font(None, 52)
        self.fonte_secundaria = pygame.font.Font(None, 40)
        
        self.tempo_decorrido = 0.0
        self.duracao_aviso = 4.0  # Ficará na tela por 4 segundos

    def process_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Permite pular o aviso apertando ESPAÇO ou ENTER
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                    self.state_manager.change_state("Intro")

    def update(self, dt):
        self.tempo_decorrido += dt
        
        # Quando o tempo acabar, vai automaticamente para a próxima tela
        if self.tempo_decorrido >= self.duracao_aviso:
            self.state_manager.change_state("Intro")

    def draw(self, surface):
        # Preenche com tela 100% preta
        surface.fill(config.COLOR_BLACK)
        w, h = surface.get_size()

        # Texto 1
        texto1 = "O objetivo do jogo é criticar as apostas e denunciar o dano que as mesmas podem causar."
        surf1 = self.fonte_principal.render(texto1, True, config.COLOR_WHITE)
        rect1 = surf1.get_rect(center=(w // 2, h // 2 - 20))
        
        # Texto 2
        texto2 = "Não aposte."
        surf2 = self.fonte_secundaria.render(texto2, True, (200, 50, 50)) # Vermelho suave
        rect2 = surf2.get_rect(center=(w // 2, h // 2 + 40))

        surface.blit(surf1, rect1)
        surface.blit(surf2, rect2)