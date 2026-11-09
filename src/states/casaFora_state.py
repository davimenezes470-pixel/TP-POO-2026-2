import pygame
import os
from states.base_state import BaseState
from utils.hud import desenhar_dinheiro

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class CasaForaState(BaseState):
    def __init__(self, game, state_manager):
        super().__init__(state_manager)
        self.game = game
        
        # Carrega a imagem do lado de fora (com tratamento de caminho seguro)
        imagem_original = pygame.image.load('assets/casaFora.png').convert()
        self.bg_image = pygame.transform.scale(imagem_original, self.game.screen.get_size())        
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.game.player)
        self.fonte_aviso = pygame.font.Font(None, 32)

    def process_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state_manager.change_state("Menu")
                elif event.key == pygame.K_c:
                    pass
                elif event.key == pygame.K_f:
                    # Ao apertar F do lado de fora, volta para o estado "Jogo" (dentro de casa)
                    self.state_manager.change_state("Jogo")

    def update(self, dt):
        self.all_sprites.update(dt)
        
        largura_tela = self.game.screen.get_width()
        
        # Mantém o jogador dentro dos limites da tela da rua
        if self.game.player.hitbox.left < 0:
            self.game.player.hitbox.left = 0
            self.game.player.pos_x = float(self.game.player.hitbox.x)
        elif self.game.player.hitbox.right > largura_tela:
            self.game.player.hitbox.right = largura_tela
            self.game.player.pos_x = float(self.game.player.hitbox.x)

    def draw(self, surface):
        surface.blit(self.bg_image, (0, 0))
        self.all_sprites.draw(surface)
        desenhar_dinheiro(surface, self.game.player.carteira.saldo)
        
        # --- DESENHA O AVISO SOBRE O JOGADOR ---
        texto = "Aperte F para entrar em casa"
        sombra = self.fonte_aviso.render(texto, True, (0, 0, 0))
        branco = self.fonte_aviso.render(texto, True, (255, 255, 255))
        
        # Usa o top do 'rect' para a mensagem ficar acima da cabeça
        x_centro = self.game.player.rect.centerx
        y_base = self.game.player.rect.top - 10
        
        rect_branco = branco.get_rect(midbottom=(x_centro, y_base))
        rect_sombra = sombra.get_rect(midbottom=(x_centro + 2, y_base + 2))
        
        surface.blit(sombra, rect_sombra)
        surface.blit(branco, rect_branco)