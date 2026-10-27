import pygame
import sys
import ctypes
import random

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass



def main():
    pygame.init()
    display = pygame.display.set_mode((1920,1080), pygame.RESIZABLE)
    pygame.display.set_caption("Demo: Tigrinho")
    clock = pygame.time.Clock()

    cor = (0,0,0)
    
    tamanho = 60
    velocidade = 5
    x = 100
    y = 100


    run = True
    while run:
        # Processar Inputs
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                run = False

        corQuadrado = (random.randint(0,250),random.randint(0,250),random.randint(0,250))
        # Atualizar estados
        teclas = pygame.key.get_pressed()
    
        if teclas[pygame.K_LEFT]:
            x -= velocidade
        if teclas[pygame.K_RIGHT]:
            x += velocidade
        if teclas[pygame.K_SPACE]:
            y-=20

        y += 10

        if y+tamanho>=1080:
            y = 1080-tamanho

        quadrado = (x,y,tamanho,tamanho)
        # Renderizar
        

        display.fill(cor)
        pygame.draw.rect(display, corQuadrado, quadrado)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

main()