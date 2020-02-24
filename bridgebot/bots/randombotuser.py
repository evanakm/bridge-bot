from game.interface import User

import random


class RandomBotUser(User):
    @staticmethod
    def play_card_from_own_hand(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history,
                                leader_history):
        return random.choice(tuple(legal_cards))

    @staticmethod
    def play_card_from_dummy_hand(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history,
                                  leader_history):
        return random.choice(tuple(legal_cards))

    @staticmethod
    def make_bid(current_player, record, legal_bids):
        return random.choice(tuple(legal_bids))
