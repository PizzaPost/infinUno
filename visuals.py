# PizzaPost magic here
import pygame

from cards import ALL_CARDS

pygame.init()


class Window:
    def __init__(self, name, debugging=False):
        self.debugging = debugging
        self.cardIndex = 0
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h
        self.name = name
        self.icon = pygame.image.load("resources/icon.png")
        self.imageFailed = False
        self.window = pygame.display.set_mode(
            (pygame.display.Info().current_w, pygame.display.Info().current_h),
            pygame.SCALED,
        )
        pygame.display.set_caption(self.name)
        pygame.display.set_icon(self.icon)
        self.running = False
        # threading.Thread(target=self.run, daemon=True).start()
        self.run()

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Exiting...")
                    self.running = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                print("Exiting...")
                self.running = False
            if (keys[pygame.K_SPACE] or self.imageFailed) and self.debugging:
                self.imageFailed = False
                self.showCard(
                    "center", "center", ALL_CARDS[self.cardIndex % len(ALL_CARDS)]
                )
                self.cardIndex += 1
                pygame.time.delay(100)

            # PER FRAME CODE HERE

            pygame.display.flip()
        quit()

    def showCard(self, x, y, card):
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
        self.window.blit(card_img, card_rect)


if __name__ == "__main__":
    window = Window("PizzaPost", debugging=True)
