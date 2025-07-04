# PizzaPost magic here
import pygame

pygame.init()


class Window:
    def __init__(self, name):
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h
        self.name = name
        self.icon = pygame.image.load("resources/icon.png")
        pg = pygame.display.set_mode()
        pygame.display.set_caption(self.name)
        pygame.display.set_icon(self.icon)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
            pygame.display.flip()


if __name__ == '__main__':
    pg = Window("PizzaPost")
    pg.run()
