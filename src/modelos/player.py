#Módulo da entidade jogável
import pygame
import config
from modelos.carteira import Carteira

class Player(pygame.sprite.Sprite):
    #Representa o personagem controlável pelo jogador, sua carteira e animações.
    def __init__(self, x, y, tracker = None):
        super().__init__()

        self.carteira = Carteira(config.SALDO_INICIAL, tracker)
        self.frame_width = 128
        self.frame_height = 128
        
        # Carrega as Sprite Sheets originais
        # (Certifique-se de que as imagens estão no mesmo diretório ou ajuste o caminho)
        sheet_idle = pygame.image.load(config.PASTA_ASSETS / "principal-idle.png").convert_alpha()
        sheet_walk = pygame.image.load(config.PASTA_ASSETS / "principal-walk.png").convert_alpha()

        # Dicionário guardando todas as animações já recortadas e espelhadas
        self.animations = {
            "idle_right": self._extrair_frames(sheet_idle, 7, espelhar=False),
            "idle_left": self._extrair_frames(sheet_idle, 7, espelhar=True),
            "walk_right": self._extrair_frames(sheet_walk, 10, espelhar=False),
            "walk_left": self._extrair_frames(sheet_walk, 10, espelhar=True),
        }

        # --- ESTADO E ANIMAÇÃO ---
        self.state = "idle_right"    
        self.olhando_direita = True    
        self.frame_index = 0.0         
        self.animation_speed = 10.0    

        # Configuração inicial exigida pelo Pygame
        self.image = self.animations[self.state][int(self.frame_index)]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-512, 0)

        # --- FÍSICA E MOVIMENTO ---
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.speed = 400  

    def _extrair_frames(self, sheet, num_frames, espelhar=False):

        #Recorta os quadros da sprite sheet.
        #Se 'espelhar=True', inverte a imagem horizontalmente para andar para a esquerda.

        frames = []
        for i in range(num_frames):
            frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            
            area_corte = pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            
            frame.blit(sheet, (0, 0), area_corte)
            
            if espelhar:
                frame = pygame.transform.flip(frame, True, False)
                
            frame = pygame.transform.scale(frame, (768, 768))

            frames.append(frame)
            
        return frames

    def _processar_controles(self, dt):
        #Lê o teclado e define o novo estado de movimento e direção.
        keys = pygame.key.get_pressed()
        em_movimento = False

        if keys[pygame.K_RIGHT]:
            self.pos_x += self.speed * dt
            self.olhando_direita = True
            em_movimento = True
        elif keys[pygame.K_LEFT]:
            self.pos_x -= self.speed * dt
            self.olhando_direita = False
            em_movimento = True

        # Atualiza a string do estado com base na ação e direção
        if em_movimento:
            self.state = "walk_right" if self.olhando_direita else "walk_left"
        else:
            self.state = "idle_right" if self.olhando_direita else "idle_left"

    def _animar(self, dt):
        #Atualiza a imagem exibida baseando-se no estado atual.
        # Avança o índice do frame baseado no tempo real (dt)
        self.frame_index += self.animation_speed * dt
        
        lista_atual = self.animations[self.state]

        # Faz a animação recomeçar (loop) quando chegar no último frame
        if self.frame_index >= len(lista_atual):
            self.frame_index = 0.0

        # Define a imagem final que o Pygame desenhará na tela
        self.image = lista_atual[int(self.frame_index)]

    def update(self, dt):
        #Método principal chamado a cada frame.
        self._processar_controles(dt)
        self._animar(dt)

        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

        self.hitbox.x = int(self.pos_x)
        self.hitbox.y = int(self.pos_y)

        self.rect.center = self.hitbox.center