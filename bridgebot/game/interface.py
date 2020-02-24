from __future__ import annotations

from typing import List, Dict, Set

from game.card import Card
from game.get_input import get_input_card, get_input_list
from abc import abstractmethod
from game.enums import Suits, Players
from game.bids import Bids

print(Bids)


class User:
    def play_card(self, partner: User, partners_cards: Set[Card], current_player: Players, dummy: Players,
                  dummy_hand: Set[Card], all_cards: Set[Card], legal_cards: Set[Card],
                  bid_history: Dict[Players, List[Bids]], card_history: Dict[Players, List[Card]],
                  leader_history: List[Players]) -> Card:
        if current_player != dummy:
            return self.play_card_from_own_hand(current_player, dummy, dummy_hand, all_cards, legal_cards,
                                                bid_history, card_history, leader_history)
        else:
            return partner.play_card_from_dummy_hand(current_player, dummy, dummy_hand, partners_cards, legal_cards,
                                                     bid_history, card_history, leader_history)

    @staticmethod
    @abstractmethod
    def play_card_from_dummy_hand(current_player: Players, dummy: Players,
                                  dummy_hand: Set[Card], all_cards: Set[Card], legal_cards: Set[Card],
                                  bid_history: Dict[Players, List[Bids]], card_history: Dict[Players, List[Card]],
                                  leader_history: List[Players]) -> Card:
        raise NotImplementedError('This is an abstract method. Please implement it before calling.'
                                  'The function play_card_from_dummy_hand has to be implemented for player ' +
                                  str(current_player))

    @staticmethod
    @abstractmethod
    def play_card_from_own_hand(current_player: Players, dummy: Players,
                                dummy_hand: Set[Card], all_cards: Set[Card], legal_cards: Set[Card],
                                bid_history: Dict[Players, List[Bids]], card_history: Dict[Players, List[Card]],
                                leader_history: List[Players]) -> Card:
        raise NotImplementedError('This is an abstract method. Please implement it before calling.'
                                  'The function play_card_from_own_hand has to be implemented for player ' +
                                  str(current_player))

    @staticmethod
    @abstractmethod
    def make_bid(current_player: Players, record: Dict[Players, List[Card]], legal_bids: List[Bids]) -> None:
        raise NotImplementedError('This is an abstract method. Please implement it before calling.'
                                  'The function play_card_from_own_hand has to be implemented for player ' +
                                  str(current_player))

    @staticmethod
    def _convert_hand_to_str(cards: List[Card]) -> str:
        card_string = ""
        for card in sorted(cards):
            card_string += str(card) + " "
        return card_string

    @staticmethod
    def _beautify_hand(cards: Set[Card]) -> str:
        res = ""

        for suit in Suits.suits():
            cards_in_suit = [card for card in cards if card.suit == suit]
            cards_in_suit.sort(key=lambda x: x.rank)

            if len(cards_in_suit) != 0:
                for card in cards_in_suit:
                    res = res + str(card).ljust(20)
                res = res + "\n"
            # else:
            #     res = res + "--"
            #     res = res + "\n"

        return res


class HumanUser(User):
    @staticmethod
    def play_card_from_own_hand(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history,
                                leader_history):
        print("Please play Player: " + str(current_player))
        print("Dummy Cards: \n" + User._beautify_hand(dummy_hand))  # Alternatively User._convert_hand_to_str
        print("Your Cards: \n" +
              User._beautify_hand(all_cards)
              )
        print("Legal Cards: \n" +
              User._beautify_hand(legal_cards)
              )

        return get_input_card(legal_cards)

    @staticmethod
    def play_card_from_dummy_hand(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history,
                                  leader_history):
        print("It is the Dummy's turn (" + str(dummy) + "). Please play Player: " + str(current_player.partner()))
        print("Dummy Cards: \n" + User._beautify_hand(dummy_hand))  # Alternatively User._convert_hand_to_str
        print("Your Cards: \n" +
              User._beautify_hand(all_cards)
              )
        print("Legal Cards: \n" +
              User._beautify_hand(legal_cards)
              )

        return get_input_card(legal_cards)

    @staticmethod
    def make_bid(current_player, record, legal_bids):
        print("Please play Player: " + str(current_player))
        print("Record: " + str(record)) # TODO stringify record
        print("Legal Bids: " + str(legal_bids))
        return get_input_list(legal_bids, "bid")

