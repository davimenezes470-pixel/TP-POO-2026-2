import pygame
import config
import random
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
        imagem_original = pygame.image.load(config.PASTA_ASSETS / "Casa-Principal.jpg").convert()
        
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

        # --- SISTEMA DE DIÁLOGOS ---
        self.dialogo_ativo = False
        self.dialogo_linhas = []
        self.dialogo_indice = 0
        
        self.dialogos_esposa = [
            ("Você vai sair de novo? As contas estão atrasadas.", "Eu vou resolver isso hoje, confia em mim."),
            ("Não aguento mais essa situação, precisamos de estabilidade.", "Só preciso de mais uma chance, eu juro."),
            ("Onde foi parar o dinheiro que deixei na gaveta?", "Eu peguei emprestado, logo eu devolvo em dobro."),
            ("Você tem passado muito tempo naquele celular...", "É só trabalho, não se preocupe com isso."),
            ("A gente costumava ser tão feliz antes de tudo isso.", "Nós vamos ser felizes de novo, é só uma fase ruim.")
        ]
        
        self.dialogos_filha = [
            ("Pai, você prometeu que ia brincar comigo hoje.", "O papai tá ocupado agora, filha. Mais tarde, tá bom?"),
            ("Meus amigos da escola disseram que você tá devendo dinheiro.", "Não dê ouvidos a eles, as pessoas falam demais."),
            ("Você vai no meu torneio no fim de semana?", "Se eu conseguir um dinheiro até lá, eu vou."),
            ("Pai, por que a mãe tava chorando ontem à noite?", "Problemas de adulto, princesa. Vai ficar tudo bem."),
            ("Eu fiz um desenho pra você, olha!", "Que lindo, filha. Deixa o papai ver isso depois, tá?")
        ]

    def iniciar_dialogo(self, lista_dialogos, nome_npc):
        dialogo_escolhido = random.choice(lista_dialogos)
        self.dialogo_linhas = [
            (nome_npc, dialogo_escolhido[0]),
            ("Você", dialogo_escolhido[1])
        ]
        self.dialogo_indice = 0
        self.dialogo_ativo = True

    def process_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                
                # Avança ou fecha o diálogo
                if self.dialogo_ativo and event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
                    self.dialogo_indice += 1
                    if self.dialogo_indice >= len(self.dialogo_linhas):
                        self.dialogo_ativo = False
                    return # Bloqueia outras ações enquanto fala

                if event.key == pygame.K_ESCAPE:
                    self.state_manager.change_state("Menu")
                elif event.key == pygame.K_c and not self.dialogo_ativo:
                    self.state_manager.change_state("Celular")
                elif event.key == pygame.K_f and not self.dialogo_ativo:
                    self.state_manager.change_state("CasaFora")
                elif event.key == pygame.K_e and not self.dialogo_ativo:
                    # Inicia diálogo se estiver perto
                    if self.game.player.hitbox.colliderect(self.filha.hitbox):
                        self.iniciar_dialogo(self.dialogos_filha, "Filha")
                    elif self.game.player.hitbox.colliderect(self.esposa.hitbox):
                        self.iniciar_dialogo(self.dialogos_esposa, "Esposa")
                        
    def update(self, dt):
        
        if not self.dialogo_ativo:
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

    def _desenhar_caixa_dialogo(self, surface):
        w, h = surface.get_size()
        altura_caixa = int(h * 0.25)
        caixa = pygame.Surface((w, altura_caixa))
        caixa.set_alpha(220)
        caixa.fill((10, 10, 12))
        
        y_topo = h - altura_caixa
        surface.blit(caixa, (0, y_topo))
        pygame.draw.line(surface, (200, 200, 200), (0, y_topo), (w, y_topo), 2)
        
        nome, texto = self.dialogo_linhas[self.dialogo_indice]
        
        cor_nome = (200, 200, 100) if nome == "Você" else (100, 200, 200)
        surf_nome = self.fonte_aviso.render(nome + ":", True, cor_nome)
        surface.blit(surf_nome, (50, y_topo + 30))
        
        surf_texto = self.fonte_aviso.render(texto, True, (255, 255, 255))
        surface.blit(surf_texto, (50, y_topo + 80))
        
        surf_dica = self.fonte_aviso.render("Aperte E para continuar", True, (150, 150, 150))
        surface.blit(surf_dica, (w - surf_dica.get_width() - 50, h - 40))
        
    def draw(self, surface):
        surface.blit(self.bg_image, (0, 0))
        self.all_sprites.draw(surface)

        # HUD de dinheiro (canto superior direito)
        desenhar_dinheiro(surface, self.game.player.carteira.saldo)

        if self.dialogo_ativo:
            self._desenhar_caixa_dialogo(surface)
        else:
            # Só desenha os avisos flutuantes se não estiver no meio de uma conversa
            if self.game.player.hitbox.colliderect(self.filha.hitbox):
                self._desenhar_aviso(surface, "Aperte E para falar com filha", self.filha.rect)
                
            if self.game.player.hitbox.colliderect(self.esposa.hitbox):
                self._desenhar_aviso(surface, "Aperte E para falar com esposa", self.esposa.rect)

        w, h = surface.get_size()
        texto_celular = "Aperte C para abrir o celular"
        sombra_cel = self.fonte_aviso.render(texto_celular, True, (0, 0, 0))
        branco_cel = self.fonte_aviso.render(texto_celular, True, (200, 200, 220))

        # Posiciona com 20 pixels de margem da esquerda e de baixo
        surface.blit(sombra_cel, (22, h - 48))
        surface.blit(branco_cel, (20, h - 50))