import pygame
from states.base_state import BaseState
import config

class NoiteState(BaseState):
    def __init__(self, game, state_manager):
        super().__init__(state_manager)
        self.game = game
        self.tempo = 0.0
        self.duracao = 2.0  # Tempo em segundos da noite
        
        self.fonte_titulo = pygame.font.Font(None, 60)
        self.fonte_sub = pygame.font.Font(None, 36)

        # Carrega a imagem do quarto e ajusta para o tamanho da tela
        try:
            img = pygame.image.load(config.PASTA_ASSETS / "casaNoiteCutscene.jpg").convert()
            self.bg_image = pygame.transform.scale(img, self.game.screen.get_size())
        except:
            self.bg_image = None
            
        # Cria a "película" escura (0 = invisível, 255 = totalmente opaco)
        self.camada_escura = pygame.Surface(self.game.screen.get_size())
        self.camada_escura.set_alpha(210) 
        self.camada_escura.fill((0, 0, 0))

    def process_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._amanhecer()

    def update(self, dt):
        self.tempo += dt
        if self.tempo >= self.duracao:
            self._amanhecer()
            
    def _amanhecer(self):
        self.tempo = 0.0
        self.game.tracker.avancar_dia()
        if self.game.tracker.dias_sem_apostar >= 7:
            self.state_manager.change_state("CutsceneVitoria")
        else:
            self.state_manager.change_state("Jogo")

    def draw(self, surface):
        w, h = surface.get_size()
        
        # Desenha a imagem de fundo primeiro, depois escurece por cima
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
            surface.blit(self.camada_escura, (0, 0))
        else:
            surface.fill((8, 8, 12))  # Fundo de segurança se a imagem falhar
        
        # Textos da noite
        txt_dia = f"Fim do Dia {self.game.tracker.dia_atual}"
        titulo = self.fonte_titulo.render(txt_dia, True, (220, 220, 220))
        surface.blit(titulo, titulo.get_rect(center=(w // 2, h // 2 - 20)))
        
        sub = self.fonte_sub.render("Ainda não fiquei milionário...", True, (120, 120, 120))
        surface.blit(sub, sub.get_rect(center=(w // 2, h // 2 + 30)))