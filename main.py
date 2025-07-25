import random

import pygame

import sys, os

# This makes sure the parent directory is on path, allowing imports from inside the infinUno package, while also allowing other scripts to use this folder as a package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infinUno import cards, visuals, players # type: ignore

pygame.init()


def show_deck(window, deck):
    deckImage = visuals.deckImage(window, deck)
    window.window.blit(deckImage, (window.width // 2 - deckImage.get_width() // 2, window.height // 2 - deckImage.get_height() // 2))


if __name__ == "__main__":
    window = visuals.Window("InfinUno")
    deck = cards.Deck()
    running = True
    while running:
        window.window.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit(0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
            pygame.quit()
            exit(0)
        if keys[pygame.K_SPACE]:
            deck.clear()
            for x in range(10):
                deck.draw()
        show_deck(window, deck)
        # PER FRAME CODE HERE

        pygame.display.flip()
