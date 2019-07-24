from deck import Deck

from enums import Players, Contracts, Doubles, Vulnerabilities
import cardplay
from get_input import get_input_enum
from scoring import get_score_from_result

if __name__ == "__main__":
    deck = Deck()
    deck.shuffle()

    contract = get_input_enum(Contracts, "contract")
    doubled = get_input_enum(Doubles, "doubled status")
    declarer = get_input_enum(Players, "declarer")
    vulnerability = get_input_enum(Vulnerabilities, "vulnerability")
    vulnerability = vulnerability.is_declarer_vulnerable(declarer)

    trick_winners = cardplay.play(deck.deal(), contract, declarer)

    score = get_score_from_result(contract, doubled, trick_winners, vulnerability)

    print(score)
