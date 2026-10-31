import pygame
import config
from states.base_state import BaseState

# Importe a classe Player (ajuste o caminho se ela estiver dentro de uma pasta, ex: from entities.player import Player)
from modelos.player import Player 

class GameState(BaseState):

    def __init__(self, game, state_manager):
        super().__init__(state_manager)
        self.game = game
        
        # 1. Cria o grupo de sprites que vai gerenciar todas as entidades da tela
        self.all_sprites = pygame.sprite.Group()

        # 3. Adiciona o personagem ao grupo
        self.all_sprites.add(self.game.player)

    def process_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # ESC faz voltar ao menu
                if event.key == pygame.K_ESCAPE:
                    self.state_manager.change_state("Menu")
                if event.key == pygame.K_c:
                    self.state_manager.change_state("Celular")

    def update(self, dt):
        # Chama o método update() de todos os sprites no grupo (incluindo o Player)
        # É aqui que a movimentação e as animações do personagem acontecem
        self.all_sprites.update(dt)

    def draw(self, surface):
        # Desenha todos os sprites do grupo na tela
        self.all_sprites.draw(surface)