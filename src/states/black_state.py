import pygame

import config
from states.base_state import BaseState
from modelos.blackjack import MesaBlackjack, APOSTANDO, JOGADOR, DEALER, FIM

COR_FELTRO = (14, 92, 54)
COR_BORDA = (212, 175, 55)
COR_CARTA = (248, 246, 240)
COR_VERMELHO = (190, 30, 40)
COR_PRETO = (25, 25, 30)
COR_VERSO = (30, 60, 140)
COR_AJUDA = (200, 225, 210)

DELAY_DEALER = 1.0   # segundos entre cada carta do dealer
APOSTA_MINIMA = 10
PASSO_APOSTA = 10


class BlackjackState(BaseState):
    """Tela do Blackjack: desenha a mesa, lê os comandos e anima o dealer.

    A regra do jogo fica em MesaBlackjack; aqui só há apresentação e input.
    """

    def __init__(self, game, state_manager):
        super().__init__(state_manager)
        self.game = game
        self.mesa = MesaBlackjack(self.game.player.carteira)

        self.valor_aposta = 50
        self.mensagem = "Escolha o valor da aposta e pressione ESPAÇO."
        self._tempo_dealer = 0.0
        self._fontes = {}

    def _fonte(self, tamanho):
        """Cache de fontes: a tela pode mudar de tamanho (F11, maximizar)."""
        tamanho = max(12, int(tamanho))
        if tamanho not in self._fontes:
            self._fontes[tamanho] = pygame.font.Font(None, tamanho)
        return self._fontes[tamanho]

    def _aposta_minima(self):
        return min(APOSTA_MINIMA, self.mesa.saldo)

    def process_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            fase = self.mesa.fase
            if event.key == pygame.K_ESCAPE:
                if fase in (APOSTANDO, FIM):
                    self.state_manager.change_state("Celular")
            elif fase == APOSTANDO:
                self._input_apostando(event.key)
            elif fase == JOGADOR:
                self._input_jogador(event.key)
            elif fase == FIM:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self._proxima_rodada()

    def _input_apostando(self, tecla):
        if tecla == pygame.K_UP:
            self.valor_aposta = min(self.valor_aposta + PASSO_APOSTA, self.mesa.saldo)
        elif tecla == pygame.K_DOWN:
            self.valor_aposta = max(self.valor_aposta - PASSO_APOSTA, self._aposta_minima())
        elif tecla == pygame.K_a:
            # ALL-IN: aposta todo o saldo e já dá as cartas
            self.valor_aposta = self.mesa.saldo
            self._input_apostando(pygame.K_SPACE)
        elif tecla in (pygame.K_SPACE, pygame.K_RETURN):
            try:
                self.mesa.apostar(self.valor_aposta)
            except ValueError as erro:
                self.mensagem = str(erro)
                return
            self.game.tracker.registrar_jogada("Blackjack")
            self._tempo_dealer = 0.0
            self.mensagem = "Sua vez: H pedir, S parar" + (", D dobrar." if self.mesa.pode_dobrar else ".")
            self._sincronizar()

    def _input_jogador(self, tecla):
        try:
            if tecla == pygame.K_h:
                self.mesa.pedir()
            elif tecla == pygame.K_s:
                self.mesa.parar()
            elif tecla == pygame.K_d:
                self.mesa.dobrar()
            else:
                return
        except ValueError as erro:
            self.mensagem = str(erro)
            return
        self._tempo_dealer = 0.0
        if self.mesa.fase == JOGADOR:
            self.mensagem = "Sua vez: H pedir, S parar."
        self._sincronizar()

    def _proxima_rodada(self):
        self.mesa.nova_rodada()
        self.valor_aposta = max(self._aposta_minima(), min(self.valor_aposta, self.mesa.saldo))
        self.mensagem = "Escolha o valor da aposta e pressione ESPAÇO."

    def update(self, dt):
        if self.mesa.fase != DEALER:
            return

        self._tempo_dealer += dt
        if self._tempo_dealer >= DELAY_DEALER:
            self._tempo_dealer = 0.0
            self.mesa.dealer_passo()  # compra uma carta ou encerra a rodada
            self._sincronizar()
        elif self.mesa.fase == DEALER:
            self.mensagem = "Vez do dealer..."

    def _sincronizar(self):
        """Atualiza a mensagem quando a rodada termina."""
        mesa = self.mesa
        if mesa.fase != FIM:
            return

        if mesa.resultado == "blackjack":
            texto = f"Blackjack! Você ganhou {mesa.liquido}!"
        elif mesa.resultado == "vitoria":
            quem = "Dealer estourou! " if mesa.dealer.estourou else ""
            texto = f"{quem}Você ganhou {mesa.liquido}!"
        elif mesa.resultado == "empate":
            texto = "Empate. Aposta devolvida."
        else:
            quem = "Você estourou! " if mesa.jogador.estourou else "O dealer venceu. "
            texto = f"{quem}Você perdeu {-mesa.liquido}."

        if mesa.saldo <= 0:
            texto += " Sem saldo!"
            self.game.agendar_game_over()
        else:
            texto += " ESPAÇO: nova rodada."
        self.mensagem = texto

    @staticmethod
    def _desenhar_naipe(surface, naipe, cx, cy, s, cor):
        """Desenha o naipe com formas simples (a fonte padrão não tem ♥♠♦♣)."""
        r = s * 0.27
        if naipe == "ouros":
            pygame.draw.polygon(surface, cor, [
                (cx, cy - s * 0.5), (cx + s * 0.36, cy),
                (cx, cy + s * 0.5), (cx - s * 0.36, cy),
            ])
        elif naipe == "copas":
            pygame.draw.circle(surface, cor, (cx - r, cy - r * 0.6), r)
            pygame.draw.circle(surface, cor, (cx + r, cy - r * 0.6), r)
            pygame.draw.polygon(surface, cor, [
                (cx - r * 1.93, cy - r * 0.35), (cx + r * 1.93, cy - r * 0.35),
                (cx, cy + s * 0.5),
            ])
        elif naipe == "espadas":
            pygame.draw.circle(surface, cor, (cx - r, cy + r * 0.2), r)
            pygame.draw.circle(surface, cor, (cx + r, cy + r * 0.2), r)
            pygame.draw.polygon(surface, cor, [
                (cx - r * 1.93, cy), (cx + r * 1.93, cy), (cx, cy - s * 0.5),
            ])
            pygame.draw.polygon(surface, cor, [
                (cx, cy), (cx - r * 0.6, cy + s * 0.5), (cx + r * 0.6, cy + s * 0.5),
            ])
        else:  # paus
            rr = r * 0.85
            pygame.draw.circle(surface, cor, (cx, cy - r * 0.95), rr)
            pygame.draw.circle(surface, cor, (cx - r * 1.0, cy + r * 0.35), rr)
            pygame.draw.circle(surface, cor, (cx + r * 1.0, cy + r * 0.35), rr)
            pygame.draw.polygon(surface, cor, [
                (cx, cy), (cx - r * 0.6, cy + s * 0.5), (cx + r * 0.6, cy + s * 0.5),
            ])

    def _desenhar_carta(self, surface, carta, x, y, cw, ch):
        rect = pygame.Rect(x, y, cw, ch)
        pygame.draw.rect(surface, COR_CARTA, rect, border_radius=8)
        pygame.draw.rect(surface, COR_PRETO, rect, 2, border_radius=8)

        cor = COR_VERMELHO if carta.cor == "vermelho" else COR_PRETO
        fonte = self._fonte(cw * 0.36)
        txt = fonte.render(carta.valor, True, cor)
        surface.blit(txt, (x + cw * 0.08, y + ch * 0.04))
        
        txt180 = pygame.transform.rotate(txt, 180)
        surface.blit(txt180, txt180.get_rect(bottomright=(x + cw * 0.92, y + ch * 0.96)))

        self._desenhar_naipe(surface, carta.naipe, x + cw * 0.5, y + ch * 0.52, cw * 0.46, cor)
        self._desenhar_naipe(surface, carta.naipe, x + cw * 0.18, y + ch * 0.30, cw * 0.16, cor)

    def _desenhar_verso(self, surface, x, y, cw, ch):
        rect = pygame.Rect(x, y, cw, ch)
        pygame.draw.rect(surface, COR_CARTA, rect, border_radius=8)
        interno = rect.inflate(-cw * 0.14, -cw * 0.14)
        pygame.draw.rect(surface, COR_VERSO, interno, border_radius=6)
        pygame.draw.rect(surface, COR_BORDA, interno.inflate(-10, -10), 2, border_radius=4)
        pygame.draw.rect(surface, COR_PRETO, rect, 2, border_radius=8)

    def _desenhar_mao(self, surface, mao, x, y, cw, ch, esconder_segunda=False):
        passo = int(cw * 0.80)
        for i, carta in enumerate(mao.cartas):
            cx = x + i * passo
            if esconder_segunda and i == 1:
                self._desenhar_verso(surface, cx, y, cw, ch)
            else:
                self._desenhar_carta(surface, carta, cx, y, cw, ch)

    def _linha(self, surface, texto, pos, tamanho=32, cor=config.COLOR_WHITE):
        surface.blit(self._fonte(tamanho).render(texto, True, cor), pos)

    def draw(self, surface):
        w, h = surface.get_size()
        mesa = self.mesa
        surface.fill(COR_FELTRO)

        cw = int(min(w * 0.09, h * 0.17))
        ch = int(cw * 1.4)
        x0 = int(w * 0.06)

        #  dealer 
        y_dealer = int(h * 0.14)
        escondida = mesa.fase in (JOGADOR,) and not mesa.dealer_revelada
        self._linha(surface, "DEALER", (x0, y_dealer - int(h * 0.07)), int(h * 0.05))
        if mesa.dealer.cartas:
            self._desenhar_mao(surface, mesa.dealer, x0, y_dealer, cw, ch, esconder_segunda=escondida)
            total = f"{mesa.dealer.cartas[0].pontos}+?" if escondida else str(mesa.dealer.valor)
            self._linha(surface, total, (x0, y_dealer + ch + 10), int(h * 0.05), COR_BORDA)

        #  jogador 
        y_jogador = int(h * 0.58)
        self._linha(surface, "VOCÊ", (x0, y_jogador - int(h * 0.07)), int(h * 0.05))
        if mesa.jogador.cartas:
            self._desenhar_mao(surface, mesa.jogador, x0, y_jogador, cw, ch)
            self._linha(surface, str(mesa.jogador.valor), (x0, y_jogador + ch + 10), int(h * 0.05), COR_BORDA)

        #  painel lateral 
        x = int(w * 0.68)
        self._linha(surface, "BLACKJACK", (x, int(h * 0.08)), int(h * 0.075))
        self._linha(surface, f"Saldo: {mesa.saldo}", (x, int(h * 0.20)))
        if mesa.fase == APOSTANDO:
            self._linha(surface, f"Aposta: {self.valor_aposta}", (x, int(h * 0.26)))
        else:
            self._linha(surface, f"Aposta: {mesa.aposta}", (x, int(h * 0.26)))

        largura_max = w - x - int(w * 0.03)
        self._desenhar_texto_quebrado(surface, self.mensagem, x, int(h * 0.36), largura_max, COR_BORDA)

        ajuda = self._texto_ajuda()
        for n, linha in enumerate(ajuda):
            self._linha(surface, linha, (x, int(h * 0.62) + n * 32), 26, COR_AJUDA)

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

    def _texto_ajuda(self):
        fase = self.mesa.fase
        if fase == APOSTANDO:
            return ["SETAS CIMA/BAIXO: valor da aposta", "ESPAÇO: dar as cartas", "A: ALL-IN (aposta todo o saldo)", "ESC: voltar ao menu"]
        if fase == JOGADOR:
            linhas = ["H: pedir carta", "S: parar"]
            if self.mesa.pode_dobrar:
                linhas.append("D: dobrar a aposta")
            return linhas
        if fase == FIM:
            return ["ESPAÇO: continuar", "ESC: voltar ao menu"]
        return []