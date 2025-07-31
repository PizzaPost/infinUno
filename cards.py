import copy
import os
import random

import pygame

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
        name: str = "",
        cmod: str = "",
        affects: list = [1],
        affectInvert: bool = False,
        skip: bool = False,
        reverse: bool = False,
        color: str = "",
        nextColor: list[str] = [],
        corner: str = "",
        image: list[str] = getImageList(
            ["resources/cards/unoBG.png", "resources/cards/unoFG.png"]
        ),
        weight: float = 1.0,
    ):
        """
        Initializes a new Card object.

        Parameters
        ----------
        name : str, optional
            The name of the card. Defaults to an empty string.
        cmod : str, optional
            The count modifier. This is a string which will be appended to "drawCounter = drawCounter" and executed to modify the draw counter accordingly. cmod will be split at every comma and each part will be executed separately in order. Defaults to an empty string.
        affects : list, optional
            A list of player indices that this card will affect. Defaults to [1], which is the next player in line.
        affectInvert : bool, optional
            Whether to invert the list of affected players. Defaults to False.
        skip : bool, optional
            Whether to skip the turns of all affected players as long as this card is the top card. Defaults to False.
        reverse : bool, optional
            Whether to reverse the order of play after playing this card. Defaults to False.
        color : str, optional
            The color of the card. Defaults to an empty string, which means the card has no color.
        nextColor : list[str], optional
            A list of colors that the next card must be. Defaults to an empty list, which means there is no color requirement.
        corner : str, optional
            The corner of the card. Used to allow playing cards with the same corner on top of this card, even if they don't meet the color requirement. Defaults to an empty string, which means the card has no extra corner allowance.
        image : list[str], optional
            A list of image paths to load and overlay on top of each other. Will be turned into a pygame.Surface on initialization. Any path will be rendered below the next. Defaults to a list containing the paths to the Uno background and foreground images.
        weight : float, optional
            The weight of the card. This can be used to determine the probability of drawing this card. Defaults to 1.0.

        Returns
        -------
        None
        """
        pass
        self.name = name
        self.cmod = cmod
        self.affects = affects
        self.affectInvert = affectInvert
        self.skip = skip
        self.reverse = reverse
        self.color = color
        self.nextColor = nextColor if nextColor != [] else [color]
        self.corner = corner
        self.weight = weight

        img = loadResource(image[0]).convert_alpha()
        for img_path in image[1:]:
            try:
                overlay_img = loadResource(img_path).convert_alpha()
                img.blit(overlay_img, (0, 0))
            except Exception as e:
                img = loadResource("resources/icon.png").convert_alpha()
                break
        self.image = img

    def __deepcopy__(self, memo={}):
        # Custom deepcopy to avoid copying pygame.Surface
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == "image":
                setattr(result, k, v)  # shallow copy for pygame.Surface
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def loadResource(img_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isabs(img_path):
        img_path = os.path.join(base_dir, img_path)
    try:
        pyImage = pygame.image.load(img_path)
    except Exception as e:
        pyImage = pygame.image.load(os.path.join(base_dir, "resources/icon.png"))
    return pyImage


ALL_CARDS = []

for color in ["red", "blue", "green", "yellow", "purple"]:
    for i in range(10):
        ALL_CARDS.append(
            Card(
                name=color + str(i),
                color=color,
                corner=str(i),
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
            cmod="+2",
            skip=True,
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
            cmod="+1",
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
            cmod="-1",
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
        cmod="+4",
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
        cmod="*4",
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
        cmod="*2",
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
        cmod="/2",
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

ALL_CARDS.append(
    Card(
        name="plus10",
        color="choice",
        cmod="+10",
        skip=True,
        image=getImageList(
            [
                "resources/cards/base/multicolored.png",
                "resources/cards/mini_card/uncolored.png",
                "resources/cards/corners/plu10.png",
            ]
        ),
    )
)

ALL_CARDS.append(
    Card(
        name="-10",
        color="choice",
        cmod="-10",
        affects=[0],
        skip=True,
        image=getImageList(
            [
                "resources/cards/base/multicolored.png",
                "resources/cards/mini_card/uncolored.png",
                "resources/cards/corners/min10.png",
            ]
        ),
    )
)

ALL_CARDS.append(
    Card(
        name="/3",
        color="choice",
        cmod="/3",
        skip=True,
        image=getImageList(
            [
                "resources/cards/base/multicolored.png",
                "resources/cards/mini_card/uncolored.png",
                "resources/cards/corners/div3.png",
            ]
        ),
    )
)

ALL_CARDS.append(
    Card(
        name="/4",
        color="choice",
        cmod="/4",
        skip=True,
        image=getImageList(
            [
                "resources/cards/base/multicolored.png",
                "resources/cards/mini_card/uncolored.png",
                "resources/cards/corners/div4.png",
            ]
        ),
    )
)

ALL_CARDS.append(
    Card(
        name="^2",
        color="choice",
        cmod="**2",
        skip=True,
        image=getImageList(
            [
                "resources/cards/base/multicolored.png",
                "resources/cards/mini_card/uncolored.png",
                "resources/cards/corners/pow2.png",
            ]
        ),
    )
)

ALL_CARDS.append(
    Card(
        name="-4",
        color="choice",
        cmod="-4",
        affects=[0],
        skip=True,
        image=getImageList(
            [
                "resources/cards/base/multicolored.png",
                "resources/cards/mini_card/uncolored.png",
                "resources/cards/corners/min4.png",
            ]
        ),
    )
)


class Deck:
    def __init__(self, cardCount: int = 0):
        self.cards = []
        if cardCount > 0:
            self.draw(cardCount)

    def add(self, cards: list[Card] | Card):
        card = cards if isinstance(cards, list) else [cards]
        self.cards.extend(card)
        self.sort()

    def remove(self, card: Card):
        if card in self.cards:
            self.cards.remove(card)

    def sort(self):
        self.cards.sort(key=lambda x: x.name)

    def drawFrom(self, index: int = 0):
        if self.cards and 0 <= index < len(self.cards):
            return self.cards.pop(index)
        return None

    def draw(self, count: int = 1):
        if count > 0:
            drawn_cards = [randomCard() for x in range(count)]
            self.add(drawn_cards)
        elif count < 0:
            for x in range(-count):
                if self.cards:
                    self.cards.pop(random.randint(0, len(self.cards) - 1))

    def clear(self):
        self.cards = []

    def count(self):
        return len(self.cards)

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return f"Deck with {len(self.cards)} cards"

    def __repr__(self):
        return f"Deck with {len(self.cards)} cards"


def randomCard():
    weights = [card.weight for card in ALL_CARDS]
    card = random.choices(ALL_CARDS, weights=weights, k=1)[0]
    return copyCard(card)


def copyCard(card):
    return card.__deepcopy__()


pygame.quit()
if __name__ == "__main__":
    print(ALL_CARDS)
