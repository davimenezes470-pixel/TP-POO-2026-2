import pygame

class Esposa(pygame.sprite.Sprite):

    def __init__(self, x, bottom_y):
        super().__init__()

        # --- TAMANHO ORIGINAL DA SPRITE ---
        self.frame_width = 128
        self.frame_height = 128
        
    
        self.tamanho_tela_w = 600
        self.tamanho_tela_h = 600

        # Carrega a spritesheet (a imagem deve chamar esposa.png na pasta assets)
        sheet = pygame.image.load("assets/esposa.png").convert_alpha()

        # Extrai os 6 frames
        self.frames = self._extrair_frames(sheet, 6)

        # Controles de animação
        self.frame_index = 0.0
        self.animation_speed = 6.0  # Velocidade da animação (quadros por segundo)

        # Imagem inicial
        self.image = self.frames[int(self.frame_index)]
        
        # O posicionamento usa 'bottomleft' para alinhar os pés dela com o chão fornecido
        self.rect = self.image.get_rect(bottomleft=(x, bottom_y))
        
        # Hitbox (tamanho de colisão reduzido nas laterais para focar no corpo)
        self.hitbox = self.rect.inflate(-300, 0)
        self.hitbox.bottomleft = (x, bottom_y)

    def _extrair_frames(self, sheet, num_frames):
        frames = []
        for i in range(num_frames):
            frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            
            area_corte = pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            frame.blit(sheet, (0, 0), area_corte)

            frame = pygame.transform.flip(frame, True, False)
            
            # Aplica a ESCALA 
            frame = pygame.transform.scale(frame, (self.tamanho_tela_w, self.tamanho_tela_h))
            
            frames.append(frame)
            
        return frames

    def update(self, dt):
        """Atualiza a animação a cada frame."""
        self.frame_index += self.animation_speed * dt
        
        if self.frame_index >= len(self.frames):
            self.frame_index = 0.0

        # Define o frame atual para o Pygame desenhar
        self.image = self.frames[int(self.frame_index)]