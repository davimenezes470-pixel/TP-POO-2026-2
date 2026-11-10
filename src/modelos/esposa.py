#Módulo da personagem NPC Esposa.
import pygame
import config

class Esposa(pygame.sprite.Sprite):
    #Representa a personagem Esposa animada no cenário interno da casa.
    def __init__(self, x, bottom_y):
        super().__init__()
        #Inicializa a sprite da Esposa alinhada ao chão especificado.
        self.frame_width = 128
        self.frame_height = 128
        self.tamanho_tela_w = 600
        self.tamanho_tela_h = 600

        sheet = pygame.image.load(config.PASTA_ASSETS / "esposa.png").convert_alpha()

        self.frames = self._extrair_frames(sheet, 6)

        self.frame_index = 0.0
        self.animation_speed = 6.0 

        self.image = self.frames[int(self.frame_index)]
        
        self.rect = self.image.get_rect(bottomleft=(x, bottom_y))
        
        self.hitbox = self.rect.inflate(-300, 0)
        self.hitbox.bottomleft = (x, bottom_y)

    def _extrair_frames(self, sheet, num_frames):
        #Recorta, espelha horizontalmente e escala os quadros da spritesheet.
        frames = []
        for i in range(num_frames):
            frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            
            area_corte = pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            frame.blit(sheet, (0, 0), area_corte)

            frame = pygame.transform.flip(frame, True, False)
            
            frame = pygame.transform.scale(frame, (self.tamanho_tela_w, self.tamanho_tela_h))
            
            frames.append(frame)
            
        return frames

    def update(self, dt):
        #Atualiza a animação a cada frame.
        self.frame_index += self.animation_speed * dt
        
        if self.frame_index >= len(self.frames):
            self.frame_index = 0.0

        self.image = self.frames[int(self.frame_index)]