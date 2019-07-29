from enums import Players, Suits, Ranks
from bridgehand import BridgeHand

from card import Card

import random


class Deck:
    def __init__(self):
        self.__card_indices = list(range(52))

    def shuffle(self):
        for i in range(51, 0, -1):
            j = random.randint(0, i)  # So as not to bias certain permutations
            if j == i:
                continue
            self.__card_indices[i], self.__card_indices[j] = self.__card_indices[j], self.__card_indices[i]

    def deal(self):
        return Deck.__deal(self.__card_indices)

    def get_card_indices(self):
        return self.__card_indices

    @staticmethod
    def generate_card_from_index(index):
        if index not in range(52):
            raise ValueError("index must be an integer between 0 and 51 inclusive.")
        return Card(Suits.suits()[int(index / 13)], Ranks.ranks()[index % 13])

    @staticmethod
    def __generate_bridge_hand(card_indices, start, stop):
        return BridgeHand.generate_complete_hand([
            Deck.generate_card_from_index(card_index) for card_index in card_indices[start:stop]
        ])

    @staticmethod
    def __deal(card_indices):
        """
        Deal out a deck of cards

        Parameters
        ----------
        card_indices: `list` [`int`]
            The list of cards between 0 and 51 inclusive

        Returns
        -------
        hands: `dict` [`Players`, `BridgeHand`]
            The bridge hands to be played
        """

        if not isinstance(card_indices, list):
            raise Exception("cards must be a list of ints")

        for card in card_indices:
            if card not in range(52):
                raise Exception("Index must be an integer between 0 and 51 inclusive.")

        # Weird python indexing, but it's right
        return {
            Players.NORTH: Deck.__generate_bridge_hand(card_indices, 0, 13),
            Players.EAST: Deck.__generate_bridge_hand(card_indices, 13, 26),
            Players.SOUTH: Deck.__generate_bridge_hand(card_indices, 26, 39),
            Players.WEST: Deck.__generate_bridge_hand(card_indices, 39, 52)
        }
