import pygame

_fontes = {}


def _fonte(tamanho):
    if tamanho not in _fontes:
        _fontes[tamanho] = pygame.font.Font(None, tamanho)
    return _fontes[tamanho]


def desenhar_dinheiro(surface, saldo):
    """Mostra o saldo no canto superior direito, dentro da moldura da cena."""
    w, h = surface.get_size()
    fonte = _fonte(int(h * 0.06))   # acompanha o tamanho da janela

    texto = f"R${saldo:,}"
    sombra = fonte.render(texto, True, (0, 0, 0))
    branco = fonte.render(texto, True, (255, 255, 255))

    x = w - branco.get_width() - int(w * 0.04)   # afasta da borda direita
    y = int(h * 0.075)                            # abaixo da moldura do teto
    surface.blit(sombra, (x + 2, y + 2))
    surface.blit(branco, (x, y))