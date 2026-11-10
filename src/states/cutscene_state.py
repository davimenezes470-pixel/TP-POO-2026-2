import pygame
import os
from states.base_state import BaseState

class CutsceneState(BaseState):
    def __init__(self, game, state_manager, cenas, proximo_estado):
        super().__init__(state_manager)
        self.game = game
        self.cenas = cenas
        self.proximo_estado = proximo_estado
        self.indice_atual = 0
        
        self.fonte_texto = pygame.font.Font(None, 40)
        self.fonte_dica = pygame.font.Font(None, 24)
        
        # Faz o cache das imagens e redimensiona para a tela do jogo
        self.imagens_carregadas = {}
        for cena in self.cenas:
            caminho = cena.get("imagem")
            if caminho and caminho not in self.imagens_carregadas:
                try:
                    img = pygame.image.load(caminho).convert()
                    self.imagens_carregadas[caminho] = pygame.transform.scale(img, self.game.screen.get_size())
                except FileNotFoundError:
                    print(f"[Aviso] Imagem de cutscene não encontrada: {caminho}")
                    self.imagens_carregadas[caminho] = None

    def process_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                    self._avancar()
                elif event.key == pygame.K_ESCAPE:
                    self._pular()

    def _avancar(self):
        """Passa para a próxima cena. Se acabar, vai para o estado destino."""
        self.indice_atual += 1
        if self.indice_atual >= len(self.cenas):
            self._pular()

    def _pular(self):
        """Pula a cutscene inteira e reseta o índice."""
        self.indice_atual = 0 
        if self.proximo_estado == "Menu":
            self.game.novo_jogo()
        self.state_manager.change_state(self.proximo_estado)

    def update(self, dt):
        pass

    def _desenhar_texto_quebrado(self, surface, texto, x_centro, y_centro, largura_max):
        """Quebra o texto e centraliza múltiplas linhas na tela."""
        linha, linhas = "", []
        for palavra in texto.split():
            tentativa = f"{linha} {palavra}".strip()
            if self.fonte_texto.size(tentativa)[0] <= largura_max:
                linha = tentativa
            else:
                linhas.append(linha)
                linha = palavra
        if linha:
            linhas.append(linha)
        
        # Centraliza o bloco inteiro de texto no eixo Y
        altura_linha = 40
        y_inicial = y_centro - ((len(linhas) * altura_linha) // 2)
        
        for n, l in enumerate(linhas):
            txt_surf = self.fonte_texto.render(l, True, (255, 255, 255))
            txt_rect = txt_surf.get_rect(center=(x_centro, y_inicial + n * altura_linha))
            surface.blit(txt_surf, txt_rect)

    def draw(self, surface):
        w, h = surface.get_size()
        surface.fill((0, 0, 0))

        cena_atual = self.cenas[self.indice_atual]
        caminho_img = cena_atual.get("imagem")
        
        # Desenha a imagem de fundo, se existir
        if caminho_img and self.imagens_carregadas.get(caminho_img):
            surface.blit(self.imagens_carregadas[caminho_img], (0, 0))

        texto = cena_atual.get("texto", "")
        if texto:
            # Caixa preta translúcida (Alpha 200 de 255)
            altura_caixa = int(h * 0.25)
            caixa = pygame.Surface((w, altura_caixa))
            caixa.set_alpha(200)
            caixa.fill((10, 10, 12))
            
            y_topo_caixa = h - altura_caixa
            surface.blit(caixa, (0, y_topo_caixa))
            pygame.draw.line(surface, (200, 200, 200), (0, y_topo_caixa), (w, y_topo_caixa), 2)

            # Desenha o texto principal
            self._desenhar_texto_quebrado(
                surface, 
                texto, 
                x_centro=w // 2, 
                y_centro=y_topo_caixa + (altura_caixa // 2), 
                largura_max=int(w * 0.8)
            )

        # Controles
        dica = self.fonte_dica.render("ESPAÇO: Continuar   |   ESC: Pular", True, (150, 150, 150))
        surface.blit(dica, dica.get_rect(bottomright=(w - 20, h - 20)))