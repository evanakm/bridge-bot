from enums import Players
from cards import BridgeHand

import random


class Deck:
    def __init__(self):
        self.card_indices = list(range(52))

    def shuffle(self):
        for i in range(51, 0, -1):
            j = random.randint(0, i)  # So as not to bias certain permutations
            if j == i:
                continue
            self.card_indices[i], self.card_indices[j] = self.card_indices[j], self.card_indices[i]

    def deal(self):
        return Deck.__deal(self.card_indices)

    @staticmethod
    def __deal(cards):
        """
        Deal out a deck of cards

        Parameters
        ----------
        cards: `list` [`int`]
            The list of cards between 0 and 51 inclusive

        Returns
        -------
        hands: `dict` [`Players`, `BridgeHand`]
            The bridge hands to be played
        """

        if not isinstance(cards, list):
            raise Exception("cards must be a list of ints")

        for card in cards:
            if card not in range(52):
                raise Exception("Index must be an integer between 0 and 51 inclusive.")

        # Weird python indexing, but it's right
        return {
            Players.NORTH: BridgeHand(cards[0:13]),
            Players.EAST: BridgeHand(cards[13:26]),
            Players.SOUTH: BridgeHand(cards[26:39]),
            Players.WEST: BridgeHand(cards[39:52]),
        }