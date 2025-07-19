# PizzaPost magic here
import pygame

from cards import ALL_CARDS

pygame.init()


class Window:
    def __init__(self, name):
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h
        self.name = name
        self.icon = pygame.image.load("resources/icon.png")
        self.window = pygame.display.set_mode(
            (pygame.display.Info().current_w, pygame.display.Info().current_h),
            pygame.SCALED,
        )
        pygame.display.set_caption(self.name)
        pygame.display.set_icon(self.icon)
        self.running = False

    def showCard(self, x, y, angle, card):
        # Display a card image at (x, y). If x or y is "center", center the card.
        # Assemble the card image by overlaying all image paths in card.image
        try:
            base_img = pygame.image.load(card.image[0]).convert_alpha()
            for img_path in card.image[1:]:
                overlay_img = pygame.image.load(img_path).convert_alpha()
                base_img.blit(overlay_img, (0, 0))
            card_img = base_img
        except Exception as e:
            print(f"Error loading card image: {e}")
            self.imageFailed = True
            return
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
        self.window.blit(rotated_card, rotated_card_rect)


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
            window.showCard("center", "center", 0, ALL_CARDS[cardIndex % len(ALL_CARDS)])
            cardIndex += 1
            pygame.time.delay(100)

        # PER FRAME CODE HERE

        pygame.display.flip()
