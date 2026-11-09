import pygame
import config
from states.base_state import BaseState
from modelos.player import Player
from utils.hud import desenhar_dinheiro 

class GameState(BaseState):

    def __init__(self, game, state_manager):
        super().__init__(state_manager)
        self.game = game
        
        # --- BACKGROUND (IMAGEM E ESCALA) ---
        # 1. Carrega a imagem original (o .convert() melhora muito a performance para fundos opacos)
        imagem_original = pygame.image.load("assets/Casa-Principal.jpg").convert()
        
        # 2. Obtém o tamanho atual da tela (definido lá no config.py e na classe Game)
        tamanho_tela = self.game.screen.get_size()
        
        # 3. Escala a imagem (de 1920x1080) para o tamanho exato da janela do jogo (ex: 1280x720)
        self.bg_image = pygame.transform.scale(imagem_original, tamanho_tela)
        
        # --- GRUPOS DE SPRITES ---
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.game.player)

    def process_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state_manager.change_state("Menu")
                elif event.key == pygame.K_c:
                    self.state_manager.change_state("Celular")
                elif event.key == pygame.K_f:
                    # Vai para o lado de fora
                    self.state_manager.change_state("CasaFora")

    def update(self, dt):
        self.all_sprites.update(dt)
        
        # --- LÓGICA DE COLISÃO COM AS BORDAS LATERAIS (USANDO A HITBOX) ---
        largura_tela = self.game.screen.get_width()
        
        # Borda Esquerda: testa o lado esquerdo da HITBOX
        if self.game.player.hitbox.left < 0:
            self.game.player.hitbox.left = 0
            self.game.player.pos_x = float(self.game.player.hitbox.x) 
            
        # Borda Direita: testa o lado direito da HITBOX
        elif self.game.player.hitbox.right > largura_tela:
            self.game.player.hitbox.right = largura_tela
            self.game.player.pos_x = float(self.game.player.hitbox.x)
        
    def draw(self, surface):
        surface.blit(self.bg_image, (0, 0))
        self.all_sprites.draw(surface)

        # HUD de dinheiro (canto superior direito)
        desenhar_dinheiro(surface, self.game.player.carteira.saldo)
        
        # DEBUG (Apague depois)
        # Vermelho: O tamanho total da imagem (a sobra)
        #pygame.draw.rect(surface, (255, 0, 0), self.game.player.rect, 1)
        # Verde: A Hitbox real de colisão (o corpo)
        #pygame.draw.rect(surface, (0, 255, 0), self.game.player.hitbox, 2)