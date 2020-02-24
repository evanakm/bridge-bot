from __future__ import annotations
from enum import Enum

from typing import List

from game.enums import Players, Doubles, Contracts, Team, Pass


class FullContract:
    def __init__(self, contract: Union[Contracts, None], doubled: Union[Doubles, None], declarer: Union[Players, None],
                 passout: bool = False, start_of_auction: bool = False):
        self.contract = contract
        self.doubled = doubled
        self.declarer = declarer
        self.passout = passout
        self.start_of_auction = start_of_auction

        if not isinstance(passout, bool):
            raise TypeError("passout must be of type bool")

        if not isinstance(start_of_auction, bool):
            raise TypeError("start_of_auction must be of type bool")

        if passout or start_of_auction:
            return

        if not isinstance(contract, Contracts):
            raise TypeError("contract must be of enum Contracts")
        if not isinstance(doubled, Doubles):
            raise TypeError("doubled must be of enum Doubles")
        if not isinstance(declarer, Players):
            raise TypeError("declarer must be of type Players")

    @staticmethod
    def start_of_auction_generator() -> FullContract:
        return FullContract(None, None, None, False, True)

    @staticmethod
    def passout_generator() -> FullContract:
        return FullContract(None, None, None, True, False)


# Compares to a contract, so can't go into enum
class Bids(Enum):
    ONE_CLUB = Contracts.ONE_CLUB
    ONE_DIAMOND = Contracts.ONE_DIAMOND
    ONE_HEART = Contracts.ONE_HEART
    ONE_SPADE = Contracts.ONE_SPADE
    ONE_NO_TRUMP = Contracts.ONE_NO_TRUMP
    TWO_CLUBS = Contracts.TWO_CLUBS
    TWO_DIAMONDS = Contracts.TWO_DIAMONDS
    TWO_HEARTS = Contracts.TWO_HEARTS
    TWO_SPADES = Contracts.TWO_SPADES
    TWO_NO_TRUMP = Contracts.TWO_NO_TRUMP
    THREE_CLUBS = Contracts.THREE_CLUBS
    THREE_DIAMONDS = Contracts.THREE_DIAMONDS
    THREE_HEARTS = Contracts.THREE_HEARTS
    THREE_SPADES = Contracts.THREE_SPADES
    THREE_NO_TRUMP = Contracts.THREE_NO_TRUMP
    FOUR_CLUBS = Contracts.FOUR_CLUBS
    FOUR_DIAMONDS = Contracts.FOUR_DIAMONDS
    FOUR_HEARTS = Contracts.FOUR_HEARTS
    FOUR_SPADES = Contracts.FOUR_SPADES
    FOUR_NO_TRUMP = Contracts.FOUR_NO_TRUMP
    FIVE_CLUBS = Contracts.FIVE_CLUBS
    FIVE_DIAMONDS = Contracts.FIVE_DIAMONDS
    FIVE_HEARTS = Contracts.FIVE_HEARTS
    FIVE_SPADES = Contracts.FIVE_SPADES
    FIVE_NO_TRUMP = Contracts.FIVE_NO_TRUMP
    SIX_CLUBS = Contracts.SIX_CLUBS
    SIX_DIAMONDS = Contracts.SIX_DIAMONDS
    SIX_HEARTS = Contracts.SIX_HEARTS
    SIX_SPADES = Contracts.SIX_SPADES
    SIX_NO_TRUMP = Contracts.SIX_NO_TRUMP
    SEVEN_CLUBS = Contracts.SEVEN_CLUBS
    SEVEN_DIAMONDS = Contracts.SEVEN_DIAMONDS
    SEVEN_HEARTS = Contracts.SEVEN_HEARTS
    SEVEN_SPADES = Contracts.SEVEN_SPADES
    SEVEN_NO_TRUMP = Contracts.SEVEN_NO_TRUMP
    PASS = Pass.PASS
    DOUBLE = Doubles.DOUBLE
    REDOUBLE = Doubles.REDOUBLE

    @staticmethod
    def bids() -> List[Bids]:
        return [
            Bids.ONE_CLUB,      Bids.ONE_DIAMOND,       Bids.ONE_HEART,     Bids.ONE_SPADE,     Bids.ONE_NO_TRUMP,
            Bids.TWO_CLUBS,     Bids.TWO_DIAMONDS,      Bids.TWO_HEARTS,    Bids.TWO_SPADES,    Bids.TWO_NO_TRUMP,
            Bids.THREE_CLUBS,   Bids.THREE_DIAMONDS,    Bids.THREE_HEARTS,  Bids.THREE_SPADES,  Bids.THREE_NO_TRUMP,
            Bids.FOUR_CLUBS,    Bids.FOUR_DIAMONDS,     Bids.FOUR_HEARTS,   Bids.FOUR_SPADES,   Bids.FOUR_NO_TRUMP,
            Bids.FIVE_CLUBS,    Bids.FIVE_DIAMONDS,     Bids.FIVE_HEARTS,   Bids.FIVE_SPADES,   Bids.FIVE_NO_TRUMP,
            Bids.SIX_CLUBS,     Bids.SIX_DIAMONDS,      Bids.SIX_HEARTS,    Bids.SIX_SPADES,    Bids.SIX_NO_TRUMP,
            Bids.SEVEN_CLUBS,   Bids.SEVEN_DIAMONDS,    Bids.SEVEN_HEARTS,  Bids.SEVEN_SPADES,  Bids.SEVEN_NO_TRUMP,
            Bids.PASS,          Bids.DOUBLE,            Bids.REDOUBLE
        ]

    @staticmethod
    def _is_sufficient_bid(bid: Bids, bidder: Players, current_contract: FullContract) -> bool:
        if not isinstance(bidder, Players):
            raise Exception("by_bidder must be a Player")

        if not isinstance(current_contract, FullContract):
            raise Exception("Must compare to a Contract")

        if current_contract.contract is None:
            return bid != Bids.DOUBLE and bid != Bids.REDOUBLE

        if bid == Bids.PASS:
            return True

        if isinstance(bid.value, Contracts):
            return current_contract.contract < bid.value

        if bid == Bids.DOUBLE:
            if current_contract.contract is None:
                # Can't double until bidding has been opened
                return False
            elif current_contract.doubled != Doubles.NONE:
                # Can only double an undoubled contract
                return False
            elif Team.player_to_team(bidder) == Team.player_to_team(current_contract.declarer):
                # Can only double if opponents have bid
                return False
            else:
                return True

        if bid == Bids.REDOUBLE:
            if current_contract.contract is None:
                # Can't redouble until a double has been made
                return False
            elif current_contract.doubled != Doubles.DOUBLE:
                # Can't redouble until a double has been made
                return False
            elif Team.player_to_team(current_contract.declarer) != Team.player_to_team(bidder):
                # Can only redouble the opponents' double
                return False
            else:
                return True

    def map_to_contract(self) -> Contracts:
        bids = self.bids()
        return Contracts.contracts()[bids.index(self)]

    @staticmethod
    def all_legal_bids(bidder: Players, current_contract: FullContract) -> List[Bids]:
        return [bid for bid in Bids.bids() if Bids._is_sufficient_bid(bid, bidder, current_contract)]

    @staticmethod
    def beautify_legal_bids(bidder: Players, current_contract: FullContract) -> str:
        legal_bids = Bids.all_legal_bids(bidder, current_contract)

        counter = 0
        res = ''
        for bid in Bids.bids():
            if bid in legal_bids:
                res = res + bid.value.value.ljust(8)
            else:
                res = res + '--'.ljust(8)

            if counter % 5 == 4:
                res = res + '\n'
            counter = counter + 1

        return res
