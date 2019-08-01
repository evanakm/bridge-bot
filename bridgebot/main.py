from deck import Deck

from enums import Players, Contracts, Doubles, Vulnerabilities
import cardplay
from scoring import get_score_from_result
from interface import HumanUser


if __name__ == "__main__":
    deck = Deck()
    deck.shuffle()

    # Todo add in bid getting
    contract = Contracts.FIVE_CLUBS # get_input_enum(Contracts, "contract")
    doubled = Doubles.DOUBLE # get_input_enum(Doubles, "doubled status")
    declarer = Players.EAST # get_input_enum(Players, "declarer")
    vulnerability = Vulnerabilities.BOTH # get_input_enum(Vulnerabilities, "vulnerability")
    vulnerability = vulnerability.is_declarer_vulnerable(declarer)

    # Todo, link in bid history
    bid_history = None

    users = {
        Players.NORTH: HumanUser(),
        Players.SOUTH: HumanUser(),
        Players.WEST: HumanUser(),
        Players.EAST: HumanUser()
    }

    trick_winners = cardplay.play(users, deck.deal(), contract, declarer, bid_history)

    score = get_score_from_result(contract, doubled, trick_winners, vulnerability)

    print(score)
