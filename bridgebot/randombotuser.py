from interface import User

import random


class RandomBotUser(User):
    @staticmethod
    def play_card(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        return random.choice(tuple(legal_cards))