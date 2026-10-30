import pygame

class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        # --- CONFIGURAÇÕES DE SPRITE ---
        self.frame_width = 128
        self.frame_height = 128
        
        # Carrega as Sprite Sheets originais
        # (Certifique-se de que as imagens estão no mesmo diretório ou ajuste o caminho)
        sheet_idle = pygame.image.load("assets/principal-idle.png").convert_alpha()
        sheet_walk = pygame.image.load("assets/principal-walk.png").convert_alpha()

        # Dicionário guardando todas as animações já recortadas e espelhadas
        self.animations = {
            "idle_right": self._extrair_frames(sheet_idle, 7, espelhar=False),
            "idle_left": self._extrair_frames(sheet_idle, 7, espelhar=True),
            "walk_right": self._extrair_frames(sheet_walk, 10, espelhar=False),
            "walk_left": self._extrair_frames(sheet_walk, 10, espelhar=True),
        }

        # --- ESTADO E ANIMAÇÃO ---
        self.state = "idle_right"      # Estado inicial
        self.olhando_direita = True    # Controla a direção em que parou
        self.frame_index = 0.0         # Índice do quadro atual (decimal para fluidez com dt)
        self.animation_speed = 10.0    # Velocidade da animação (10 quadros por segundo)

        # Configuração inicial exigida pelo Pygame
        self.image = self.animations[self.state][int(self.frame_index)]
        self.rect = self.image.get_rect(topleft=(x, y))

        # --- FÍSICA E MOVIMENTO ---
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.speed = 300  # Pixels por segundo

    def _extrair_frames(self, sheet, num_frames, espelhar=False):
        """
        Recorta os quadros da sprite sheet.
        Se 'espelhar=True', inverte a imagem horizontalmente para andar para a esquerda.
        """
        frames = []
        for i in range(num_frames):
            # 1. Cria a superfície transparente para o quadro
            frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            
            # 2. Define qual área da sheet será recortada (Avança de 128 em 128 no eixo X)
            area_corte = pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            
            # 3. Desenha o recorte na superfície em branco
            frame.blit(sheet, (0, 0), area_corte)
            
            # 4. Aplica o espelhamento se for para a esquerda
            if espelhar:
                # flip(imagem, eixo_x, eixo_y)
                frame = pygame.transform.flip(frame, True, False)
                
            # Opcional: Se a imagem ficar muito grande na tela, você pode escalá-la aqui:
            frame = pygame.transform.scale(frame, (256, 256))

            frames.append(frame)
            
        return frames

    def _processar_controles(self, dt):
        """Lê o teclado e define o novo estado de movimento e direção."""
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
        """Atualiza a imagem exibida baseando-se no estado atual."""
        # Avança o índice do frame baseado no tempo real (dt)
        self.frame_index += self.animation_speed * dt
        
        lista_atual = self.animations[self.state]

        # Faz a animação recomeçar (loop) quando chegar no último frame
        if self.frame_index >= len(lista_atual):
            self.frame_index = 0.0

        # Define a imagem final que o Pygame desenhará na tela
        self.image = lista_atual[int(self.frame_index)]

    def update(self, dt):
        """Método principal chamado a cada frame."""
        self._processar_controles(dt)
        self._animar(dt)

        # Sincroniza o Float de posição com o Rect (Inteiro) para o Pygame desenhar no lugar certo
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)