import pygame

class Filha(pygame.sprite.Sprite):

    def __init__(self, x, bottom_y):
        super().__init__()

        # --- TAMANHO ORIGINAL DA SPRITE ---
        self.frame_width = 128
        self.frame_height = 128
        

        # Modifique os valores abaixo para escalar a personagem.
        self.tamanho_tela_w = 512
        self.tamanho_tela_h = 512

        # Carrega a spritesheet (a imagem que está na pasta assets)
        sheet = pygame.image.load("assets/filha.png").convert_alpha()

        # Extrai os 9 frames
        self.frames = self._extrair_frames(sheet, 9)

        # Controles de animação
        self.frame_index = 0.0
        self.animation_speed = 8.0  # Quadros por segundo da animação

        # Imagem e Retângulo inicial
        self.image = self.frames[int(self.frame_index)]
        
        # A posição (x, y) vem do GameState e é aplicada aqui:
        self.rect = self.image.get_rect(bottomleft=(x, bottom_y))
        
        # Hitbox (opcional, para colisão ou caso queira ajustar o "corpo" dela depois)
        self.hitbox = self.rect.inflate(-300, 0)
        self.hitbox.bottomleft = (x, bottom_y)

    def _extrair_frames(self, sheet, num_frames):
        frames = []
        for i in range(num_frames):
            # Cria a superfície vazia para recortar
            frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            
            # Área do recorte na imagem original (avança de 128 em 128)
            area_corte = pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            frame.blit(sheet, (0, 0), area_corte)
            
            # Aplica a ESCALA para o tamanho que ela terá na tela
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