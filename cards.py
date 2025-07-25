import random
import pygame
import os

pygame.init()
pygame.display.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)


def getImageList(extraImages: list[str] = []) -> list[str]:
    images = []
    images.extend(extraImages)
    images.append("resources/cards/frame.png")

    return images


class Card:
    def __init__(
        self,
        name: str,
        add: int = 0,
        mult: float = 1.0,
        affects: list = [1],
        skip: bool = False,
        reverse: bool = False,
        color: str = "",
        nextColor: str = "",
        image: list[str] = getImageList(
            ["resources/cards/unoBG.png", "resources/cards/unoFG.png"]
        ),
    ):
        self.name = name
        self.add = add
        self.mult = mult
        self.affects = affects
        self.skip = skip
        self.reverse = reverse
        self.color = color
        self.nextColor = nextColor if nextColor is not None else color

        img = self.loadResource(image[0]).convert_alpha()
        for img_path in image[1:]:
            try:
                overlay_img = self.loadResource(img_path).convert_alpha()
                img.blit(overlay_img, (0, 0))
            except Exception as e:
                img = self.loadResource("resources/icon.png").convert_alpha()
                break
        self.image = img

    def loadResource(self, img_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.isabs(img_path):
            img_path = os.path.join(base_dir, img_path)
        return pygame.image.load(img_path)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


ALL_CARDS = []

for color in ["red", "blue", "green", "yellow", "purple"]:
    for i in range(10):
        ALL_CARDS.append(
            Card(
                name=color + str(i),
                color=color,
                image=getImageList(
                    [
                        f"resources/cards/base/{color}.png",
                        f"resources/cards/mini_card/{color}.png",
                        f"resources/cards/corners/{i}.png",
                    ]
                ),
            )
        )

    ALL_CARDS.append(
        Card(
            name=color + "skip",
            color=color,
            skip=True,
            image=getImageList(
                [
                    f"resources/cards/base/{color}.png",
                    f"resources/cards/mini_card/{color}.png",
                    f"resources/cards/corners/skip.png",
                ]
            ),
        )
    )

    ALL_CARDS.append(
        Card(
            name=color + "reverse",
            color=color,
            reverse=True,
            image=getImageList(
                [
                    f"resources/cards/base/{color}.png",
                    f"resources/cards/mini_card/{color}.png",
                    f"resources/cards/corners/reverse.png",
                ]
            ),
        )
    )

    ALL_CARDS.append(
        Card(
            name=color + "+2",
            color=color,
            add=2,
            image=getImageList(
                [
                    f"resources/cards/base/{color}.png",
                    f"resources/cards/mini_card/{color}.png",
                    "resources/cards/corners/plu2.png",
                ]
            ),
        )
    )

    ALL_CARDS.append(
        Card(
            name=color + "+1",
            color=color,
            skip=True,
            add=1,
            image=getImageList(
                [
                    f"resources/cards/base/{color}.png",
                    f"resources/cards/mini_card/{color}.png",
                    "resources/cards/corners/plu1.png",
                ]
            ),
        )
    )

    ALL_CARDS.append(
        Card(
            name=color + "-1",
            color=color,
            add=-1,
            affects=[0],
            image=getImageList(
                [
                    f"resources/cards/base/{color}.png",
                    f"resources/cards/mini_card/{color}.png",
                    "resources/cards/corners/min1.png",
                ]
            ),
        )
    )

ALL_CARDS.append(
    Card(
        name="wild",
        color="choice",
        image=getImageList(
            [
                "resources/cards/base/multicolored.png",
                "resources/cards/mini_card/uncolored.png",
                "resources/cards/corners/questionmark.png",
            ]
        ),
    )
)

ALL_CARDS.append(
    Card(
        name="+4",
        color="choice",
        add=4,
        skip=True,
        image=getImageList(
            [
                "resources/cards/base/multicolored.png",
                "resources/cards/mini_card/uncolored.png",
                "resources/cards/corners/plu4.png",
            ]
        ),
    )
)

ALL_CARDS.append(
    Card(
        name="*4",
        color="choice",
        mult=4,
        skip=True,
        image=getImageList(
            [
                "resources/cards/base/multicolored.png",
                "resources/cards/mini_card/uncolored.png",
                "resources/cards/corners/mul4.png",
            ]
        ),
    )
)

ALL_CARDS.append(
    Card(
        name="*2",
        color="choice",
        mult=2,
        skip=True,
        image=getImageList(
            [
                "resources/cards/base/multicolored.png",
                "resources/cards/mini_card/uncolored.png",
                "resources/cards/corners/mul2.png",
            ]
        ),
    )
)

ALL_CARDS.append(
    Card(
        name="/2",
        color="choice",
        mult=1 / 2,
        skip=True,
        image=getImageList(
            [
                "resources/cards/base/multicolored.png",
                "resources/cards/mini_card/uncolored.png",
                "resources/cards/corners/div2.png",
            ]
        ),
    )
)


class Deck:
    def __init__(self):
        self.cards = []

    def add_card(self, card: Card):
        self.cards.append(card)

    def sort(self):
        self.cards.sort(key=lambda x: (x.color, x.name))

    def drawFrom(self, index: int = 0):
        if self.cards and 0 <= index < len(self.cards):
            return self.cards.pop(index)
        return None

    def draw(self, count: int = 1):
        drawn_cards = [random.choice(ALL_CARDS) for _ in range(count)]
        self.cards.extend(drawn_cards)

    def clear(self):
        self.cards = []

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return f"Deck with {len(self.cards)} cards"

    def __repr__(self):
        return f"Deck with {len(self.cards)} cards"


pygame.quit()
if __name__ == "__main__":
    print(ALL_CARDS)
