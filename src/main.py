import pygame
import sys
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

def main():
    pygame.init()
    display = pygame.display.set_mode((1920,1080), pygame.RESIZABLE)
    pygame.display.set_caption("Demo: Tigrinho")
    clock = pygame.time.Clock()

    run = True
    while run:
        # Processar Inputs
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                run = False
            #elif evento.type == pygame.KEYDOWN:
        # Atualizar estados

        # Renderizar
        cor = (0,0,0)
        display.fill(cor)
        pygame.draw.rect(display, (150,150,150), (960, 100, 75,75))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

main()