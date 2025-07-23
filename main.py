import random

import pygame

import cards
import visuals

pygame.init()

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
        for x in range(len(deck.cards)):
            window.showCard(
                x=(
                    window.width // 2
                    - (
                        (len(deck.cards) - 1)
                        * (
                            0
                            if len(deck.cards) == 1
                            else (
                                (
                                    window.width
                                    - 20
                                    - pygame.image.load(
                                        "resources/cards/frame.png"
                                    ).get_width()
                                )
                                / (len(deck.cards) - 1)
                                if len(deck.cards)
                                * pygame.image.load(
                                    "resources/cards/frame.png"
                                ).get_width()
                                > window.width * 2 - 20
                                else pygame.image.load(
                                    "resources/cards/frame.png"
                                ).get_width()
                                // 2
                            )
                        )
                        + pygame.image.load("resources/cards/frame.png").get_width()
                    )
                    // 2
                )
                + x
                * (
                    0
                    if len(deck.cards) == 1
                    else (
                        (
                            window.width
                            - 20
                            - pygame.image.load("resources/cards/frame.png").get_width()
                        )
                        / (len(deck.cards) - 1)
                        if len(deck.cards)
                        * pygame.image.load("resources/cards/frame.png").get_width()
                        > window.width * 2 - 20
                        else pygame.image.load("resources/cards/frame.png").get_width()
                        // 2
                    )
                ),
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
                    else ((len(deck.cards) - 1) / 2 - x)
                    * (2 * 20)
                    / (len(deck.cards) - 1)
                ),
                card=deck.cards[x],
            )
        # PER FRAME CODE HERE

        pygame.display.flip()
