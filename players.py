from . import cards


class Player:
    def __init__(self, playerInstance=None, name="", hand=None):
        self.name = playerInstance.name if playerInstance is not None else name
        self.hand = hand if hand is not None else cards.Deck(7)
        self.bot = False
        self.player = playerInstance
        self.deck_message = None

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
