import pygame

from engine import GraphicEngine

if __name__ == "__main__":
    display = pygame.display.set_mode((900, 700))
    engine = GraphicEngine(display)
    pygame.mouse.set_cursor(*pygame.cursors.arrow)
    pygame.display.set_caption("Робот")
    engine.run()
