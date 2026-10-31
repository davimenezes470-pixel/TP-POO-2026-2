import math

import pygame

import config
from states.base_state import BaseState
from modelos.slots import (
    MesaSlots, FITA, LINHAS, PAGAMENTO, NUM_ROLOS, NUM_LINHAS,
)

COR_FUNDO = (38, 14, 18)
COR_QUADRO = (28, 18, 20)
COR_BORDA = (212, 175, 55)
COR_AJUDA = (180, 180, 190)
# Visual provisório (sem assets): rótulo + cor. Troque por imagens quando tiver sprites.
ESTILO_SIMBOLO = {
    "cereja": ("CER", (200, 30, 60)),
    "limao": ("LIM", (200, 180, 30)),
    "sino": ("SINO", (225, 150, 30)),
    "tigre": ("TIGRE", (235, 100, 20)),
    "sete": ("7", (60, 120, 255)),
}

SALDO_INICIAL = 1000
APOSTA_MINIMA = 5       # por linha (o custo da rodada é x5 linhas)
PASSO_APOSTA = 5
VEL_GIRO = 22.0         # símbolos por segundo enquanto o rolo gira
TEMPO_BASE = 0.9        # segundos até o 1º rolo começar a frear
TEMPO_ENTRE_ROLOS = 0.5
TEMPO_FREIO = 0.45


class Rolo:
    """Só animação. `pos` = índice (float) do símbolo do topo; diminui => símbolos descem."""

    def __init__(self, tamanho_fita):
        self.n = tamanho_fita
        self.pos = 0.0
        self.modo = "parado"    # girando | freando | parado
        self._t = 0.0
        self._parar_em = 0.0
        self._alvo = 0
        self._inicio = 0.0
        self._dist = 0.0

    def iniciar(self, alvo_topo, parar_em):
        self._alvo = alvo_topo % self.n
        self._parar_em = parar_em
        self._t = 0.0
        self.modo = "girando"

    def update(self, dt):
        if self.modo == "girando":
            self._t += dt
            self.pos = (self.pos - VEL_GIRO * dt) % self.n
            if self._t >= self._parar_em:
                self.modo, self._t = "freando", 0.0
                self._inicio = self.pos
                # +1 volta completa para dar tempo de frear suavemente
                self._dist = (self.pos - self._alvo) % self.n + self.n
        elif self.modo == "freando":
            self._t += dt
            t = min(self._t / TEMPO_FREIO, 1.0)
            suave = 1 - (1 - t) ** 3  # ease-out cúbico, igual à roleta
            self.pos = (self._inicio - self._dist * suave) % self.n
            if t >= 1.0:
                self.pos, self.modo = float(self._alvo), "parado"


class SlotsState(BaseState):
    """Tela do Tigrinho: desenha os rolos, anima o giro e lê os comandos.

    A regra do jogo fica em MesaSlots; aqui só há apresentação e input.
    """

    def __init__(self, game, state_manager):
        super().__init__(state_manager)
        self.game = game
        self.mesa = MesaSlots(saldo_inicial=SALDO_INICIAL)
        self.rolos = [Rolo(len(FITA)) for _ in range(NUM_ROLOS)]

        self.valor_aposta = 10
        self.mensagem = "Escolha o valor da aposta e pressione ESPAÇO."
        self.girando = False
        self._relogio = 0.0
        self._fontes = {}

        # Modo teste (tecla T): força o símbolo da linha do meio (tecla X escolhe qual)
        self.modo_teste = False
        self._simbolos = list(PAGAMENTO)
        self.simbolo_forcado = 0

    def _fonte(self, tamanho):
        """Cache de fontes: a tela pode mudar de tamanho (F11, maximizar)."""
        tamanho = max(12, int(tamanho))
        if tamanho not in self._fontes:
            self._fontes[tamanho] = pygame.font.Font(None, tamanho)
        return self._fontes[tamanho]

    # ---------- entrada ----------
    def _aposta_maxima(self):
        return max(APOSTA_MINIMA, self.mesa.saldo // len(LINHAS))

    def process_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE and not self.girando:
                self.state_manager.change_state("Celular")
            elif self.girando:
                continue  # bloqueia mudanças durante o giro
            elif event.key == pygame.K_UP:
                self.valor_aposta = min(self.valor_aposta + PASSO_APOSTA, self._aposta_maxima())
            elif event.key == pygame.K_DOWN:
                self.valor_aposta = max(self.valor_aposta - PASSO_APOSTA, APOSTA_MINIMA)
            elif event.key == pygame.K_a:
                # ALL-IN: aposta o máximo possível (saldo // linhas) e já gira
                self.valor_aposta = self._aposta_maxima()
                self._iniciar_giro()
            elif event.key == pygame.K_t:
                self.modo_teste = not self.modo_teste
            elif event.key == pygame.K_x and self.modo_teste:
                self.simbolo_forcado = (self.simbolo_forcado + 1) % len(self._simbolos)
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._iniciar_giro()

    # ---------- lógica da animação ----------
    def _iniciar_giro(self):
        if self.mesa.saldo < self.mesa.custo_de(APOSTA_MINIMA):
            self.mesa.reiniciar(SALDO_INICIAL)
            self.valor_aposta = 10
            self.mensagem = "Saldo reiniciado. Escolha a aposta e pressione ESPAÇO."
            return

        try:
            self.mesa.apostar(self.valor_aposta)
        except ValueError as erro:
            self.mensagem = str(erro)
            return

        forcadas = None
        if self.modo_teste:
            simbolo = self._simbolos[self.simbolo_forcado]
            forcadas = [self.mesa.rolos.parada_do_simbolo(simbolo)] * NUM_ROLOS
        resultado = self.mesa.sortear(forcadas)  # resultado já decidido; a animação só o revela

        for i, rolo in enumerate(self.rolos):
            # a parada p mostra fita[p-1], fita[p], fita[p+1]: o topo é p-1
            rolo.iniciar(resultado.paradas[i] - 1, TEMPO_BASE + i * TEMPO_ENTRE_ROLOS)
        self.girando = True
        self.mensagem = "Girando..."

    def update(self, dt):
        self._relogio += dt
        if not self.girando:
            return

        for rolo in self.rolos:
            rolo.update(dt)

        if all(r.modo == "parado" for r in self.rolos):
            self.girando = False
            n = len(self.mesa.resultado.vitorias)
            liquido = self.mesa.liquidar()
            if n:
                self.mensagem = f"{n} linha(s) premiada(s)! Você ganhou {liquido}!"
            elif liquido == 0:
                self.mensagem = "Empate. Aposta devolvida."
            else:
                self.mensagem = f"Não foi dessa vez. Você perdeu {-liquido}."
            if self.mesa.saldo < self.mesa.custo_de(APOSTA_MINIMA):
                self.mensagem += " Sem saldo: ESPAÇO para recomeçar."
            self.valor_aposta = max(APOSTA_MINIMA, min(self.valor_aposta, self._aposta_maxima()))

    # ---------- desenho ----------
    def _desenhar_simbolo(self, surface, simbolo, rect):
        rotulo, cor = ESTILO_SIMBOLO[simbolo]
        pygame.draw.rect(surface, cor, rect.inflate(-rect.w * 0.1, -rect.h * 0.1), border_radius=12)
        txt = self._fonte(rect.h * 0.34).render(rotulo, True, config.COLOR_WHITE)
        surface.blit(txt, txt.get_rect(center=rect.center))

    def _linha(self, surface, texto, pos, tamanho=32, cor=config.COLOR_WHITE):
        surface.blit(self._fonte(tamanho).render(texto, True, cor), pos)

    def _desenhar_texto_quebrado(self, surface, texto, x, y, largura_max, cor):
        fonte = self._fonte(32)
        linha, linhas = "", []
        for palavra in texto.split():
            tentativa = f"{linha} {palavra}".strip()
            if fonte.size(tentativa)[0] <= largura_max:
                linha = tentativa
            else:
                linhas.append(linha)
                linha = palavra
        if linha:
            linhas.append(linha)
        for n, l in enumerate(linhas):
            surface.blit(fonte.render(l, True, cor), (x, y + n * 34))

    def _desenhar_rolos(self, surface, centro, celula):
        n = len(FITA)
        margem = int(celula * 0.2)
        quadro = pygame.Rect(0, 0, celula * NUM_ROLOS + 2 * margem, celula * NUM_LINHAS + 2 * margem)
        quadro.center = centro
        pygame.draw.rect(surface, COR_QUADRO, quadro, border_radius=18)
        pygame.draw.rect(surface, COR_BORDA, quadro, 5, border_radius=18)

        premiadas = set()
        resultado = self.mesa.resultado
        if not self.girando and resultado:
            for v in resultado.vitorias:
                for rolo, row in enumerate(LINHAS[v.linha]):
                    premiadas.add((rolo, row))
        piscando = int(self._relogio * 6) % 2 == 0

        for i, rolo in enumerate(self.rolos):
            coluna = pygame.Rect(quadro.left + margem + i * celula, quadro.top + margem,
                                 celula, celula * NUM_LINHAS)
            clip_antigo = surface.get_clip()
            surface.set_clip(coluna)  # símbolos não vazam da coluna
            base = math.floor(rolo.pos)
            frac = rolo.pos - base
            for r in range(-1, NUM_LINHAS + 1):
                simbolo = FITA[(base + r) % n]
                rect = pygame.Rect(coluna.left, coluna.top + int((r - frac) * celula), celula, celula)
                self._desenhar_simbolo(surface, simbolo, rect)
            surface.set_clip(clip_antigo)

            if piscando:
                for row in range(NUM_LINHAS):
                    if (i, row) in premiadas:
                        cel = pygame.Rect(coluna.left, coluna.top + row * celula, celula, celula)
                        pygame.draw.rect(surface, config.COLOR_WHITE, cel.inflate(-6, -6), 4, border_radius=12)
        return quadro

    def draw(self, surface):
        w, h = surface.get_size()
        surface.fill(COR_FUNDO)

        celula = int(min(w * 0.12, h * 0.19))
        quadro = self._desenhar_rolos(surface, (int(w * 0.32), int(h * 0.52)), celula)

        premios = "   ".join(f"{ESTILO_SIMBOLO[s][0]} x{p}" for s, p in PAGAMENTO.items())
        txt = self._fonte(24).render(f"3 iguais pagam:  {premios}", True, COR_AJUDA)
        surface.blit(txt, txt.get_rect(midtop=(quadro.centerx, quadro.bottom + 14)))

        x = int(w * 0.62)
        mesa = self.mesa
        self._linha(surface, "TIGRINHO", (x, int(h * 0.10)), 48)
        self._linha(surface, f"Saldo: {mesa.saldo}", (x, int(h * 0.20)))
        self._linha(surface, f"Aposta por linha: {self.valor_aposta}", (x, int(h * 0.26)))
        self._linha(surface, f"Custo da rodada: {mesa.custo_de(self.valor_aposta)}", (x, int(h * 0.32)))

        largura_max = w - x - int(w * 0.03)
        self._desenhar_texto_quebrado(surface, self.mensagem, x, int(h * 0.42), largura_max, COR_BORDA)

        if self.modo_teste:
            self._linha(surface, f"[TESTE] símbolo forçado: {self._simbolos[self.simbolo_forcado]}",
                        (x, int(h * 0.54)), 22, (120, 220, 120))

        ajuda = [
            "SETAS CIMA/BAIXO: valor da aposta",
            "ESPAÇO: girar",
            "A: ALL-IN (aposta o máximo e gira)",
            "T: modo teste (X: símbolo forçado)",
            "ESC: voltar ao celular",
        ]
        for n, linha in enumerate(ajuda):
            self._linha(surface, linha, (x, int(h * 0.64) + n * 30), 22, COR_AJUDA)
