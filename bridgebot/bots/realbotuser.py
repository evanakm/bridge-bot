from game.interface import User

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T


class RealBotUser(User):
    @staticmethod
    def play_card_from_own_hand(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        return random.choice(tuple(legal_cards))

    @staticmethod
    def make_bid(current_player, bid_record, legal_bids):
        return random.choice(tuple(legal_bids))
