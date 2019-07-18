from BridgeBot.cards import Deck
from BridgeBot.deal import Deal

from BridgeBot.enums import Players, Vulnerabilities, contracts
from BridgeBot.cardplay import Cardplay
from BridgeBot.get_input import get_input_enum

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
    print(Players.WEST.next_player())
    deck = Deck()
    deal = Deal(Players.NORTH, Vulnerabilities.NONE, deck.card_indices)

    contract = None
    while contract not in contracts:
        contract = input("Please enter the contract: ")

    declarer = get_input_enum(Players, "declarer")

    cardplay = Cardplay(deal.hands, contract, declarer)
