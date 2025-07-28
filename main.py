import os
import sys

import pygame

# This makes sure the parent directory is on path, allowing imports from inside the infinUno package, while also allowing other scripts to use this folder as a package.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infinUno import cards, visuals, players  # type: ignore

pygame.init()


def show_deck(window, deck):
    deckImage = visuals.deckImage(window, deck)
    window.window.blit(deckImage,
                       (window.width // 2 - deckImage.get_width() // 2,
                        window.height // 2 - deckImage.get_height() // 2))

font1 = pygame.font.Font(None, 32)
font2 = pygame.font.Font(None, 24)
font3 = pygame.font.Font(None, 16)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
text = ''
done = False
if __name__ == "__main__":
    window = visuals.Window("InfinUno")
    width=window.width
    height=window.height
    input_box = pygame.Rect(width//2 - 200, height//2-16, 400, 32)
    deck = cards.Deck()
    for x in range(10): deck.add(cards.randomCard())
    running = True
    while running:
        window.window.fill((20, 20, 20))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit(0)
            if not done:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            print(text)
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode
                            txt_surface2 = font1.render(text, True, color)
                            if txt_surface2.get_width() > input_box.width-10: text = text[:-1]
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
            pygame.quit()
            exit(0)
        txt_surface1 = font1.render("Enter the lobby password to create or join a game.", True, color)
        txt_surface2 = font1.render(text, True, color)
        window.window.blit(txt_surface1, (input_box.x, input_box.y-32))
        window.window.blit(txt_surface2, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(window.window, color, input_box, 2)
        show_deck(window, deck)
        # PER FRAME CODE HERE

        pygame.display.flip()
