from cards import Deck
from deal import Deal

from enums import Players, Vulnerabilities, Contracts
from cardplay import CardPlay
from get_input import get_input_enum

if __name__ == "__main__":
    deck = Deck()
    deal = Deal(Players.NORTH, Vulnerabilities.NONE, deck.card_indices)

    contract = get_input_enum(Contracts, "contract")

    declarer = get_input_enum(Players, "declarer")

    cardPlay = CardPlay(deal.hands, contract, declarer)
