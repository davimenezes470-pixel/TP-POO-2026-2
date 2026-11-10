#Utilitários de interface (HUD) para exibição de informações sobre a tela.
import pygame

_fontes = {}


def _fonte(tamanho):
    """Retorna uma fonte do Pygame em cache para o tamanho especificado."""
    if tamanho not in _fontes:
        _fontes[tamanho] = pygame.font.Font(None, tamanho)
    return _fontes[tamanho]


def desenhar_dinheiro(surface, saldo):
    """Mostra o saldo no canto superior direito, dentro da moldura da cena."""
    w, h = surface.get_size()
    fonte = _fonte(int(h * 0.06))  

    texto = f"R${saldo:,}"
    sombra = fonte.render(texto, True, (0, 0, 0))
    branco = fonte.render(texto, True, (255, 255, 255))

    x = w - branco.get_width() - int(w * 0.04)   
    y = int(h * 0.075)                           
    surface.blit(sombra, (x + 2, y + 2))
    surface.blit(branco, (x, y))