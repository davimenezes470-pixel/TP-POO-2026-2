import config
import pygame
from states.base_state import BaseState

COR_CORPO = (20, 20, 24)
COR_BORDA_CORPO = (80, 80, 92)
COR_TELA = (32, 36, 56)
COR_TEXTO = (255, 255, 255)
COR_DICA = (150, 155, 175)

HOME = "home"
JOGOS = "jogos"


class CelularState(BaseState):

    def __init__(self, game, state_manager):
        super().__init__(state_manager)
        self.game = game
        self.tela = HOME
        self.indice = 0
        self._fontes = {}

        # (chave, rótulo, símbolo, cor)
        self.apps_home = [
            ("jogos", "Jogos", "J", (230, 90, 70)),
            ("runs", "Runs", "R", (70, 140, 230)),
            ("ifood", "iFood", "iF", (234, 29, 44)),
            ("voltar", "Voltar", "<", (120, 120, 130)),
        ]
        # (nome do estado, rótulo, símbolo, cor)
        self.apps_jogos = [
            ("Roleta", "Roleta", "R", (200, 40, 50)),
            ("Blackjack", "Blackjack", "21", (30, 130, 80)),
            ("Tigrinho", "Tigrinho", "7", (235, 140, 30)),
        ]

        # Fundo: o quarto do jogo, desfocado e escurecido
        self._fundo_original = pygame.image.load(
            str(config.PASTA_ASSETS / "Casa-Principal.jpg")).convert()
        self._fundo_cache = None

    def _fonte(self, tamanho):
        tamanho = max(12, int(tamanho))
        if tamanho not in self._fontes:
            self._fontes[tamanho] = pygame.font.Font(None, tamanho)
        return self._fontes[tamanho]

    def _fundo(self, tamanho):
        """Quarto desfocado e escurecido. Recalcula só se a janela mudar de tamanho."""
        if self._fundo_cache is None or self._fundo_cache[0] != tamanho:
            img = pygame.transform.smoothscale(self._fundo_original, tamanho)
            # desfoque: reduz bastante e amplia de volta
            pequeno = pygame.transform.smoothscale(
                img, (max(1, tamanho[0] // 24), max(1, tamanho[1] // 24)))
            img = pygame.transform.smoothscale(pequeno, tamanho)
            # escurece (0 = claro, 255 = preto)
            sombra = pygame.Surface(tamanho)
            sombra.set_alpha(150)
            sombra.fill((0, 0, 0))
            img.blit(sombra, (0, 0))
            self._fundo_cache = (tamanho, img)
        return self._fundo_cache[1]

    def _apps_atuais(self):
        if self.tela == HOME:
            return self.apps_home
        if self.tela == JOGOS:
            return self.apps_jogos
        return []

    # ---------- entrada ----------
    def process_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            apps = self._apps_atuais()
            if event.key in (pygame.K_RIGHT, pygame.K_d) and apps:
                self.indice = (self.indice + 1) % len(apps)
            elif event.key in (pygame.K_LEFT, pygame.K_a) and apps:
                self.indice = (self.indice - 1) % len(apps)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._abrir()
            elif event.key == pygame.K_ESCAPE:
                self._voltar()

    def _abrir(self):
        if self.tela == HOME:
            chave = self.apps_home[self.indice][0]
            if chave == "jogos":
                self.tela, self.indice = JOGOS, 0
            elif chave == "runs":
                # Salva a origem e leva para o arquivo de estado real
                self.game.origem_runs = "Celular"
                self.state_manager.change_state("Runs")
            elif chave == "ifood":
                self.game.player.carteira.saldo += 500
                self.state_manager.change_state("Noite")
            else:
                self._sair()
        elif self.tela == JOGOS:
            self.state_manager.change_state(self.apps_jogos[self.indice][0])
        else:
            self._voltar()

    def _voltar(self):
        if self.tela == HOME:
            self._sair()
        else:
            self.indice = 0 if self.tela == JOGOS else 1
            self.tela = HOME

    def _sair(self):
        """Fecha o celular e volta para o mapa."""
        self.tela, self.indice = HOME, 0
        self.state_manager.change_state("Jogo")

    def update(self, dt):
        pass

    # ---------- desenho ----------
    def draw(self, surface):
        w, h = surface.get_size()
        surface.blit(self._fundo(surface.get_size()), (0, 0))

        altura = int(h * 0.90)
        largura = int(altura * 0.50)
        corpo = pygame.Rect(0, 0, largura, altura)
        corpo.center = (w // 2, h // 2)
        pygame.draw.rect(surface, COR_CORPO, corpo, border_radius=int(largura * 0.12))
        pygame.draw.rect(surface, COR_BORDA_CORPO, corpo, 3, border_radius=int(largura * 0.12))

        tela = corpo.inflate(-int(largura * 0.07), -int(largura * 0.07))
        pygame.draw.rect(surface, COR_TELA, tela, border_radius=int(largura * 0.09))

        # "notch" no topo
        notch = pygame.Rect(0, 0, int(largura * 0.28), int(largura * 0.05))
        notch.midtop = (tela.centerx, tela.top + int(largura * 0.03))
        pygame.draw.rect(surface, COR_CORPO, notch, border_radius=int(largura * 0.025))

        titulo = {HOME: "Início", JOGOS: "Jogos"}[self.tela]
        txt = self._fonte(tela.w * 0.09).render(titulo, True, COR_TEXTO)
        surface.blit(txt, txt.get_rect(midtop=(tela.centerx, tela.top + int(tela.h * 0.08))))

        self._desenhar_icones(surface, tela)

        dica = "SETAS: escolher   ENTER: abrir   ESC: voltar"
        txt = self._fonte(tela.w * 0.045).render(dica, True, COR_DICA)
        surface.blit(txt, txt.get_rect(midbottom=(tela.centerx, tela.bottom - int(tela.h * 0.03))))

    def _desenhar_icones(self, surface, tela):
        apps = self._apps_atuais()
        coluna = tela.w / len(apps)
        lado = int(coluna * 0.62)
        y = tela.top + int(tela.h * 0.28)

        for i, (_, rotulo, simbolo, cor) in enumerate(apps):
            selecionado = i == self.indice
            cx = tela.left + int(coluna * (i + 0.5))
            icone = pygame.Rect(0, y, lado, lado)
            icone.centerx = cx

            pygame.draw.rect(surface, cor, icone, border_radius=int(lado * 0.22))
            if selecionado:
                pygame.draw.rect(surface, COR_TEXTO, icone.inflate(10, 10), 4,
                                 border_radius=int(lado * 0.28))

            sim = self._fonte(lado * 0.5).render(simbolo, True, COR_TEXTO)
            surface.blit(sim, sim.get_rect(center=icone.center))

            cor_rotulo = COR_TEXTO if selecionado else COR_DICA
            rot = self._fonte(lado * 0.26).render(rotulo, True, cor_rotulo)
            surface.blit(rot, rot.get_rect(midtop=(cx, icone.bottom + 14)))