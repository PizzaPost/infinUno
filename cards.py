class Card:
    def __init__(self, name, add=0, mult=1, affects=[1], color=None, nextColor=color, image="uno.png"):
        self.name = name
        self.add = add
        self.mult = mult
        self.affects = affects
        self.color = color
        self.nextColor = nextColor
        self.image = image
