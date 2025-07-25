# PizzaPost magic here
import pygame

import sys, os

# read this comment in main.py for more info
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infinUno.cards import ALL_CARDS  # type: ignore
from infinUno import cards  # type: ignore

pygame.init()


class Window:
    def __init__(self, name, window=None):
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h
        self.name = name
        self.icon = cards.loadResource("resources/icon.png")
        self.window = pygame.display.set_mode(
            (pygame.display.Info().current_w, pygame.display.Info().current_h),
            pygame.SCALED,
        ) if window is None else window
        pygame.display.set_caption(self.name)
        pygame.display.set_icon(self.icon)
        self.running = False

    def showCard(self, x, y, angle, card, surface=None):
        # Display a card image at (x, y). If x or y is "center", center the card.
        if surface is None:
            surface = self.window
        card_img = card.image
        card_rect = card_img.get_rect()
        if x == "center":
            card_rect.x = (self.width - card_rect.width) // 2
        else:
            card_rect.x = x
        if y == "center":
            card_rect.y = (self.height - card_rect.height) // 2
        else:
            card_rect.y = y
        rotated_card = pygame.transform.rotate(card_img, angle)
        rotated_card_rect = rotated_card.get_rect(center=card_rect.center)
        surface.blit(rotated_card, rotated_card_rect)


def deckImage(window, deck):
    FRAME = cards.loadResource("resources/cards/frame.png").convert_alpha()
    surface = pygame.Surface(window.window.get_size(), pygame.SRCALPHA)
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
            surface=surface,
        )
    return surface


if __name__ == "__main__":
    window = Window("PizzaPost")
    cardIndex = 0
    imageFailed = False
    running = True
    while running:
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
        if keys[pygame.K_SPACE] or imageFailed:
            imageFailed = False
            window.showCard(
                "center", "center", 0, ALL_CARDS[cardIndex % len(ALL_CARDS)]
            )
            cardIndex += 1
            pygame.time.delay(100)

        # PER FRAME CODE HERE

        pygame.display.flip()
