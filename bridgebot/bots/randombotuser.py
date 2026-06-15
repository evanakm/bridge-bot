from bridgebot.game.interface import User
from bridgebot.game.enums import Contracts

import random


class RandomBotUser(User):
    @staticmethod
    def play_card(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        return random.choice(tuple(legal_cards))

    @staticmethod
    def bid(current_player, legal_bids, bid_history):
        opening_bids = [
            bid for bid in legal_bids
            if isinstance(bid.value, Contracts) and bid.value.determine_level() == 1
        ]

        if bid_history.current_contract.contract is None and len(opening_bids) > 0:
            return random.choice(tuple(opening_bids))

        for bid in legal_bids:
            if bid.name == "PASS":
                return bid

        return random.choice(tuple(legal_bids))
