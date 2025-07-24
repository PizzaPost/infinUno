import random

import pygame

import sys, os

# This makes sure the parent directory is on path, allowing imports from inside the infinUno package, while also allowing other scripts to use this folder as a package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from . import cards
from . import visuals

pygame.init()


def show_deck(window, deck, FRAME):
    for x in range(len(deck.cards)):
        card_spread = (
            0
            if len(deck.cards) == 1
            else (
                (window.width - 20 - FRAME.get_width()) / (len(deck.cards) - 1)
                if len(deck.cards) * FRAME.get_width() > window.width * 2 - 20
                else FRAME.get_width() // 2
            )
        )

        window.showCard(
            x=(
                window.width // 2
                - ((len(deck.cards) - 1) * card_spread + FRAME.get_width()) // 2
            )
            + x * card_spread,
            y=(
                window.height
                - window.height // 2
                + window.height // 7
                + ((x - ((len(deck.cards) - 1) / 2)) ** 2)
                * (80 / ((max((len(deck.cards) - 1), 1) / 2) ** 2))
                if window.height - window.height // 2 + window.height // 7 > 1
                else 0
            ),
            angle=(
                0
                if len(deck.cards) == 1
                else ((len(deck.cards) - 1) / 2 - x) * (2 * 20) / (len(deck.cards) - 1)
            ),
            card=deck.cards[x],
        )


if __name__ == "__main__":
    window = visuals.Window("InfinUno")
    deck = cards.Deck()
    FRAME = pygame.image.load("resources/cards/frame.png").convert_alpha()
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
        show_deck(window, deck, FRAME)
        # PER FRAME CODE HERE

        pygame.display.flip()
