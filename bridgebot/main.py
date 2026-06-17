import os
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bridgebot import bidding
from bridgebot.bots.aiplayers import RuleBasedBotUser, choose_bid_for_user
from bridgebot.game import cardplay
from bridgebot.game.deck import Deck
from bridgebot.game.enums import AuctionStatus, Players, Vulnerabilities
from bridgebot.game.scoring import get_score_from_result

NUMBER_OF_PLAYTHROUGHS = 1


def main():
    if sys.version_info[0] < 3:
        print('bridgebot only works with python 3')
        return 1

    users = {
        Players.NORTH: RuleBasedBotUser(),
        Players.SOUTH: RuleBasedBotUser(),
        Players.WEST: RuleBasedBotUser(),
        Players.EAST: RuleBasedBotUser()
    }

    for i in range(0, NUMBER_OF_PLAYTHROUGHS):
        deck = Deck()
        deck.shuffle()
        deal = deck.deal()
        vulnerability = Vulnerabilities.BOTH
        auction = bidding.Auction(Players.NORTH)

        while not auction.complete():
            current_player = auction.player
            legal_bids = auction.legal_bids()
            bid = choose_bid_for_user(
                users[current_player],
                current_player,
                deal[current_player].cards,
                legal_bids,
                auction.record,
            )
            status = auction.get_new_bid(bid)
            print(current_player.name + " bid " + bid.name)
            if status == AuctionStatus.DONE:
                break

        contract = auction.determine_full_contract()
        if contract.passout:
            print("The hand was passed out. Score is 0")
            continue

        is_vulnerable = vulnerability.is_declarer_vulnerable(contract.declarer)
        trick_winners = cardplay.play(
            users,
            deal,
            contract.contract,
            contract.declarer,
            auction.record,
        )

        score = get_score_from_result(
            contract.contract,
            contract.doubled,
            trick_winners,
            is_vulnerable,
        )

        print("The declarer " + contract.declarer.name + " has a score of " + str(score))


if __name__ == "__main__":
    sys.exit(main())
