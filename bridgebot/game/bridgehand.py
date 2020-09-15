from __future__ import annotations
from typing import List, Union, Set

from game.enums import Suits

from game.card import Card, InvalidSuitException


class CardDoesntFollowSuitException(Exception):
    pass


class WrongSizeHandException(Exception):
    pass


class DeckListNotValid(Exception):
    pass


class CardNotInHandException(Exception):
    pass


class RepeatedCardException(Exception):
    pass


class BridgeHand:
    def get_cards_of_suit(self, suit) -> Set[Card]:
        if not isinstance(suit, Suits):
            raise TypeError("suit is not of type Suits")

        return set(card for card in self.cards if card.suit == suit)

    def __add_cards_to_bridge_hand(self, cards):
        if not isinstance(cards, list):
            raise DeckListNotValid("deck_indices is not a list")

        if len(cards) > 13:
            raise WrongSizeHandException("Bridge hands must contain 13 cards.")

        for card in cards:
            self.__add_card(card)

    @staticmethod
    def generate_complete_hand(cards: List[Card]) -> BridgeHand:
        """
        Generates a hand from a list of 13 ints

        Parameters
        ----------
        cards: list
            A list of 13 Cards

        Returns
        -------
        BridgeHand containing 13 Cards

        """

        if len(cards) != 13:
            raise WrongSizeHandException("cards must contain 13 cards")
        for card in cards:
            if not isinstance(card, Card):
                raise TypeError("card is not of type Card")
        return BridgeHand(cards)

    @staticmethod
    def generate_partially_played_hand(cards: List[Card]) -> BridgeHand:
        if len(cards) > 13:
            raise WrongSizeHandException("cards must contain no more than 13 cards")
        for card in cards:
            if not isinstance(card, Card):
                raise TypeError("card is not of type Card")
        return BridgeHand(cards)

    def __init__(self, cards: List[Card]):
        if not isinstance(cards, list):
            raise DeckListNotValid("cards is not a list")

        self.cards: Set[Card] = set(cards)
        if len(cards) > 13:
            raise WrongSizeHandException("cards must contain 13 cards or less")

        if len(cards) != len(set(cards)):
            raise RepeatedCardException("At least one card is repeated")

        BridgeHand.__add_cards_to_bridge_hand(self, cards)

    def contains_card(self, card: Card) -> bool:
        """
        Returns if a card is in the hand or not

        Parameters
        ----------
        card: Card
            The card to be checked

        Returns
        -------
        card_in_hand: bool
            Whether the card is in the hand or not

        """
        if not isinstance(card, Card):
            raise TypeError("card is not of type Card")

        return card in self.cards

    def __play_card(self, card: Card):
        """
        Plays a card. This removes the card from the hand.
        Parameters
        ----------
        card: Card
            The card to be played

        Returns
        -------

        """
        if not isinstance(card, Card):
            raise TypeError("card is not of type Card")

        if not self.contains_card(card):
            raise CardNotInHandException("Hand does not contain " + card.rank.name + " of " + card.suit.name + ".")
        self.cards.remove(card)

    def __add_card(self, card: Card):
        if not isinstance(card, Card):
            raise TypeError("card is not of type Card")
        self.cards.add(card)

    def lead(self, card: Card):
        """
        Parameters
        ----------
        card: Card
            The Card that was played
        """
        if not isinstance(card, Card):
            raise TypeError("card is not of type Card")

        if not self.contains_card(card):
            raise CardNotInHandException("Hand does not contain " + card.rank.name + " of " + card.suit.name + ".")

        self.__play_card(card)

    def follow(self, led_suit: Suits, card_played: Card):
        """
        Follow a suit with a card. This function removes the card from he hand of the player.

        Parameters
        ----------
        led_suit: Suits
            A suit representing the first card played to the trick
        card_played: Card
            The Card that was played
        """

        if not isinstance(led_suit, Suits):
            raise TypeError("led_suit is not of type Suits")

        if not isinstance(card_played, Card):
            raise TypeError("card_played is not of type Card")

        if card_played.suit != led_suit:
            if len(self.get_cards_of_suit(led_suit)) != 0:
                raise CardDoesntFollowSuitException("Must follow suit if possible.")
            else:
                self.__play_card(card_played)
        else:
            self.__play_card(card_played)

    def legal_cards(self, led_suit: Union[Suits, None] = None) -> Set[Card]:
        """
        Get a list of all of a players playable cards.

        Parameters
        ----------
        led_suit: Suits or None
            The suit lead

        Returns
        -------
        playable_cards: list of Card
            A list of all of the playable cards
        """
        if not (led_suit is None or isinstance(led_suit, Suits)):
            raise InvalidSuitException("Invalid Suit")

        if not led_suit:
            return self.cards

        cards_of_lead_suit = self.get_cards_of_suit(led_suit)

        if len(cards_of_lead_suit) is not 0:
            return cards_of_lead_suit
        else:
            return self.cards
