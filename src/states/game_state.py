import pygame
import config
from states.base_state import BaseState
from modelos.esposa import Esposa
from modelos.filha import Filha
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

        base_do_pai = self.game.player.rect.bottom
       
        self.all_sprites = pygame.sprite.OrderedUpdates()
        self.filha = Filha(150, base_do_pai-110)
        self.esposa = Esposa(1200, base_do_pai-110)
        # --- GRUPOS DE SPRITES ---
        self.all_sprites.add(self.filha)
        self.all_sprites.add(self.esposa)
        self.all_sprites.add(self.game.player)
        self.fonte_aviso = pygame.font.Font(None, 32)

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

    def _desenhar_aviso(self, surface, texto, alvo_rect):
        """Método utilitário para desenhar texto com sombra sobre um personagem."""
        sombra = self.fonte_aviso.render(texto, True, (0, 0, 0))
        branco = self.fonte_aviso.render(texto, True, (255, 255, 255))
        
        # Alinha pela metade horizontal do personagem, e um pouco acima da cabeça (top)
        x_centro = alvo_rect.centerx
        y_base = alvo_rect.top - 10
        
        rect_branco = branco.get_rect(midbottom=(x_centro, y_base))
        rect_sombra = sombra.get_rect(midbottom=(x_centro + 2, y_base + 2))
        
        surface.blit(sombra, rect_sombra)
        surface.blit(branco, rect_branco)
        
    def draw(self, surface):
        surface.blit(self.bg_image, (0, 0))
        self.all_sprites.draw(surface)

        # HUD de dinheiro (canto superior direito)
        desenhar_dinheiro(surface, self.game.player.carteira.saldo)
        # Se as hitboxes do jogador e da filha se tocarem, desenha o aviso sobre ela
        if self.game.player.hitbox.colliderect(self.filha.hitbox):
            self._desenhar_aviso(surface, "Aperte E para falar com filha", self.filha.rect)
            
        # Se as hitboxes do jogador e da esposa se tocarem, desenha o aviso sobre ela
        if self.game.player.hitbox.colliderect(self.esposa.hitbox):
            self._desenhar_aviso(surface, "Aperte E para falar com esposa", self.esposa.rect)
        