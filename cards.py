class Card:
    def __init__(self, name: str, add: int = 0, mult: int = 1, affects: list[int] = [1], color: str = "", nextColor: str = "", image: str = "uno.png"):
        self.name = name
        self.add = add
        self.mult = mult
        self.affects = affects
        self.color = color
        self.nextColor = nextColor if nextColor is not None else color
        self.image = image
