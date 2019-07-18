from BridgeBot.cards import Deck
from BridgeBot.deal import Deal

from BridgeBot.enums import Players, Vulnerabilities, contracts
from BridgeBot.cardplay import Cardplay

def check_cards(cards):
    if not cards:
        deck.shuffle()
        return deck.card_indices
    elif set(cards) != set(range(52)):
        print("'cards' must be a list of integers from 0 to 51 with each number appearing once.")
        print("Generating a random deal.")
        deck.shuffle()
        return deck.card_indices


if __name__ == "__main__":
    deck = Deck()
    deal = Deal(Players.NORTH, Vulnerabilities.NONE, deck.card_indices)
