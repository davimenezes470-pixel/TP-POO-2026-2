import math

import pygame

import config
from states.base_state import BaseState
from modelos.roleta import (
    MesaRoleta, ApostaNumero, ApostaCor, ApostaParidade,
)

TAU = math.tau
COR_CASA = {
    "vermelho": (178, 30, 40),
    "preto": (20, 20, 22),
    "verde": (20, 130, 60),
}
COR_BORDA = (212, 175, 55)
DURACAO_GIRO = 5.0   # segundos
VOLTAS_EXTRAS = 5    # voltas completas antes de parar


class RoletaState(BaseState):
    """Tela da roleta: desenha a roda, anima o giro e lê os comandos.

    A regra do jogo fica em MesaRoleta; aqui só há apresentação e input.
    """

    def __init__(self, game, state_manager):
        super().__init__(state_manager)
        self.game = game
        self.mesa = MesaRoleta(saldo_inicial=1000)

        self.font_num = pygame.font.Font(None, 22)
        self.font_txt = pygame.font.Font(None, 32)
        self.font_big = pygame.font.Font(None, 48)

        # Escolhas do jogador
        self.tipo_aposta = "vermelho"   # vermelho | preto | par | impar | numero
        self.numero_escolhido = 7
        self.valor_aposta = 50

        # Modo teste (tecla T): força o número sorteado (tecla X escolhe qual)
        self.modo_teste = False
        self.numero_forcado = 0

        # Animação
        self.rotacao = 0.0
        self.girando = False
        self._rot_inicio = 0.0
        self._delta = 0.0
        self._tempo = 0.0

        self.mensagem = "Escolha uma aposta e pressione ESPAÇO."
        self.ultimo_numero = None

    # ---------- entrada ----------
    def process_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE and not self.girando:
                self.state_manager.change_state("Celular")
            elif self.girando:
                continue  # bloqueia mudanças durante o giro
            elif event.key == pygame.K_r:
                self.tipo_aposta = "vermelho"
            elif event.key == pygame.K_b:
                self.tipo_aposta = "preto"
            elif event.key == pygame.K_p:
                self.tipo_aposta = "par"
            elif event.key == pygame.K_i:
                self.tipo_aposta = "impar"
            elif event.key == pygame.K_n:
                self.tipo_aposta = "numero"
            elif event.key == pygame.K_RIGHT:
                self.numero_escolhido = (self.numero_escolhido + 1) % 37
                self.tipo_aposta = "numero"
            elif event.key == pygame.K_LEFT:
                self.numero_escolhido = (self.numero_escolhido - 1) % 37
                self.tipo_aposta = "numero"
            elif event.key == pygame.K_UP:
                self.valor_aposta = min(self.valor_aposta + 10, max(self.mesa.saldo, 10))
            elif event.key == pygame.K_DOWN:
                self.valor_aposta = max(self.valor_aposta - 10, 10)
            elif event.key == pygame.K_a:
                # ALL-IN: aposta todo o saldo no tipo de aposta atual e já gira
                if self.mesa.saldo > 0:
                    self.valor_aposta = self.mesa.saldo
                    self._iniciar_giro()
            elif event.key == pygame.K_t:
                self.modo_teste = not self.modo_teste
            elif event.key == pygame.K_x and self.modo_teste:
                self.numero_forcado = (self.numero_forcado + 1) % 37
            elif event.key == pygame.K_SPACE:
                self._iniciar_giro()

    def _criar_aposta(self):
        if self.tipo_aposta in ("vermelho", "preto"):
            return ApostaCor(self.valor_aposta, self.tipo_aposta)
        if self.tipo_aposta in ("par", "impar"):
            return ApostaParidade(self.valor_aposta, self.tipo_aposta)
        return ApostaNumero(self.valor_aposta, self.numero_escolhido)

    # ---------- lógica da animação ----------
    def _iniciar_giro(self):
        try:
            self.mesa.apostar(self._criar_aposta())
        except ValueError as erro:
            self.mensagem = str(erro)
            return

        forcado = self.numero_forcado if self.modo_teste else None
        casa = self.mesa.sortear(forcado)  # resultado já decidido; a animação só o revela
        idx = self.mesa.roleta.indice_de(casa)
        step = TAU / len(self.mesa.roleta.casas)

        # A casa idx fica sob o ponteiro (topo) quando rotacao ≡ -(idx+0.5)*step
        alvo = (-(idx + 0.5) * step) % TAU
        self._rot_inicio = self.rotacao
        self._delta = ((alvo - self.rotacao) % TAU) + TAU * VOLTAS_EXTRAS
        self._tempo = 0.0
        self.girando = True
        self.mensagem = "Girando..."

    def update(self, dt):
        if not self.girando:
            return

        self._tempo += dt
        t = min(self._tempo / DURACAO_GIRO, 1.0)
        suave = 1 - (1 - t) ** 3  # ease-out cúbico: desacelera até parar
        self.rotacao = self._rot_inicio + self._delta * suave

        if t >= 1.0:
            self.girando = False
            casa = self.mesa.casa_sorteada
            liquido = self.mesa.liquidar()
            self.ultimo_numero = casa
            if liquido > 0:
                self.mensagem = f"Saiu {casa.numero} ({casa.cor}). Você ganhou {liquido}!"
            else:
                self.mensagem = f"Saiu {casa.numero} ({casa.cor}). Você perdeu {-liquido}."
            if self.mesa.saldo <= 0:
                self.mensagem += " Sem saldo."
            self.valor_aposta = max(10, min(self.valor_aposta, self.mesa.saldo))

    # ---------- desenho ----------
    @staticmethod
    def _ponto(centro, raio, angulo):
        # angulo medido em sentido horário a partir do topo
        return (centro[0] + raio * math.sin(angulo), centro[1] - raio * math.cos(angulo))

    def _desenhar_roda(self, surface, centro, raio):
        casas = self.mesa.roleta.casas
        step = TAU / len(casas)

        pygame.draw.circle(surface, COR_BORDA, centro, int(raio * 1.06))

        for i, casa in enumerate(casas):
            a0 = self.rotacao + i * step
            pontos = [centro] + [self._ponto(centro, raio, a0 + step * k / 3) for k in range(4)]
            pygame.draw.polygon(surface, COR_CASA[casa.cor], pontos)
            pygame.draw.polygon(surface, COR_BORDA, pontos, 1)

            txt = self.font_num.render(str(casa.numero), True, config.COLOR_WHITE)
            pos = self._ponto(centro, raio * 0.86, a0 + step / 2)
            surface.blit(txt, txt.get_rect(center=(int(pos[0]), int(pos[1]))))

        # miolo
        pygame.draw.circle(surface, (40, 40, 46), centro, int(raio * 0.62))
        pygame.draw.circle(surface, COR_BORDA, centro, int(raio * 0.62), 3)
        pygame.draw.circle(surface, COR_BORDA, centro, int(raio * 0.12))

        # ponteiro fixo no topo
        x, y = centro
        topo = y - raio * 1.06
        pygame.draw.polygon(surface, config.COLOR_WHITE, [
            (x, topo + 28), (x - 14, topo - 6), (x + 14, topo - 6),
        ])

    def _linha(self, surface, texto, pos, fonte=None, cor=None):
        fonte = fonte or self.font_txt
        surface.blit(fonte.render(texto, True, cor or config.COLOR_WHITE), pos)

    def draw(self, surface):
        w, h = surface.get_size()
        raio = int(min(w * 0.30, h * 0.38))
        centro = (int(w * 0.32), int(h * 0.52))
        self._desenhar_roda(surface, centro, raio)

        x = int(w * 0.62)
        self._linha(surface, "ROLETA", (x, int(h * 0.10)), self.font_big)
        self._linha(surface, f"Saldo: {self.mesa.saldo}", (x, int(h * 0.20)))
        aposta_txt = (
            f"Número {self.numero_escolhido}" if self.tipo_aposta == "numero"
            else {"vermelho": "Vermelho", "preto": "Preto", "par": "Par", "impar": "Ímpar"}[self.tipo_aposta]
        )
        self._linha(surface, f"Aposta: {aposta_txt}", (x, int(h * 0.28)))
        self._linha(surface, f"Valor: {self.valor_aposta}", (x, int(h * 0.34)))

        self._linha(surface, self.mensagem, (x, int(h * 0.46)), cor=COR_BORDA)
        if self.modo_teste:
            self._linha(surface, f"[TESTE] resultado forçado: {self.numero_forcado}",
                        (x, int(h * 0.52)), self.font_num, (120, 220, 120))

        ajuda = [
            "R / B: vermelho / preto",
            "P / I: par / ímpar",
            "N ou SETAS ESQ/DIR: número",
            "SETAS CIMA/BAIXO: valor",
            "ESPAÇO: girar",
            "A: ALL-IN (aposta todo o saldo e gira)",
            "T: modo teste (X: número forçado)",
            "ESC: voltar ao menu",
        ]
        for n, linha in enumerate(ajuda):
            self._linha(surface, linha, (x, int(h * 0.60) + n * 30), self.font_num, (180, 180, 190))
