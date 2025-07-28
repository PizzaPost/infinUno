import os
import sys
import math
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
title_size = 30
max_title_size = 128
start_animation_frame_count = 0
start_animation_duration = 250
def ease_in_out_cubic(t):
    return 4 * t**3 if t < 0.5 else 1 - (-2 * t + 2)**3 / 2
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
        if start_animation_frame_count < start_animation_duration:
            t = start_animation_frame_count / start_animation_duration
            eased = ease_in_out_cubic(t)
            title_size = int(title_size + (max_title_size - title_size) * eased)
            start_animation_frame_count += 1
            r = int(20 + (220 - 20) * eased)
            g = int(20 + (200 - 20) * eased)
            b = int(20 + (200 - 20) * eased)
        title_font = pygame.font.Font(None, title_size)
        title_font.set_bold(True)
        title_font.set_underline(True)
        txt_surface0 = title_font.render("InfinUno", True, (r, g, b))
        txt_surface1 = font1.render("Enter the lobby password to create or join a game.", True, color)
        txt_surface2 = font1.render(text, True, color)
        window.window.blit(txt_surface0, (width//2 - txt_surface0.get_width()//2, height//3))
        window.window.blit(txt_surface1, (width//2 - txt_surface1.get_width()//2, input_box.y-32))
        window.window.blit(txt_surface2, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(window.window, color, input_box, 2)
        show_deck(window, deck)
        # PER FRAME CODE HERE

        pygame.display.flip()
