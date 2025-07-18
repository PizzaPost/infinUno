import random


def getImageList(extraImages: list[str] = []) -> list[str]:
    images = []
    images.extend(extraImages)
    images.append("frame.png")

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
        image: list[str] = getImageList(["unoBG.png", "unoFG.png"]),
    ):
        self.name = name
        self.add = add
        self.mult = mult
        self.affects = affects
        self.skip = skip
        self.reverse = reverse
        self.color = color
        self.nextColor = nextColor if nextColor is not None else color
        self.image = image

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


ALL_CARDS = []

for color in ["red", "blue", "green", "yellow", "purple"]:
    for i in range(1, 10):
        ALL_CARDS.append(
            Card(
                name=color + str(i),
                color=color,
                image=getImageList([f"{color}.png", f"{i}.png"]),
            )
        )
    ALL_CARDS.append(
        Card(
            name=color + "skip",
            color=color,
            skip=True,
            image=getImageList([f"{color}.png", f"skip.png"]),
        )
    )
    ALL_CARDS.append(
        Card(
            name=color + "reverse",
            color=color,
            reverse=True,
            image=getImageList([f"{color}.png", f"reverse.png"]),
        )
    )
    ALL_CARDS.append(
        Card(
            name=color + "+2",
            color=color,
            image=getImageList([f"{color}.png", "+2.png"]),
            add=2,
        )
    )
    ALL_CARDS.append(
        Card(
            name=color + "+1",
            color=color,
            image=getImageList([f"{color}.png", "+1.png"]),
            add=1,
            skip=True,
        )
    )
    ALL_CARDS.append(
        Card(
            name=color + "-1",
            color=color,
            image=getImageList([f"{color}.png", "-1.png"]),
            add=-1,
            affects=[0],
        )
    )

ALL_CARDS.append(
    Card(
        name="wild",
        color="choice",
        image=getImageList(["base/multicolored.png", "mini_card/uncolored.png", "corners/questionmark.png"]),
    )
)
ALL_CARDS.append(
    Card(
        name="+4",
        color="choice",
        image=getImageList(
            ["base/multicolored.png", "mini_card/uncolored.png", "corners/plu4.png"]
        ),
        add=4,
        skip=True,
    )
)
ALL_CARDS.append(
    Card(
        name="*4",
        color="choice",
        image=getImageList(
            ["base/multicolored.png", "mini_card/uncolored.png", "corners/mul4.png"]
        ),
        mult=4,
        skip=True,
    )
)
ALL_CARDS.append(
    Card(
        name="*2",
        color="choice",
        image=getImageList(
            ["base/multicolored.png", "mini_card/uncolored.png", "corners/mul2.png"]
        ),
        mult=2,
        skip=True,
    )
)
ALL_CARDS.append(
    Card(
        name="/2",
        color="choice",
        image=getImageList(
            ["base/multicolored.png", "mini_card/uncolored.png", "corners/div2.png"]
        ),
        mult=1 / 2,
        skip=True,
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

    def draw(self):
        self.cards.append(random.choice(ALL_CARDS))

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return f"Deck with {len(self.cards)} cards"

    def __repr__(self):
        return f"Deck with {len(self.cards)} cards"

if __name__ == "__main__":
    print(ALL_CARDS)
