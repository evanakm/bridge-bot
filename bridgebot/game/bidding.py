from __future__ import annotations
from typing import Dict, List, Union, Tuple

from game.enums import Players, Strains, AuctionStatus, Doubles, Contracts, Team, InvalidPlayerException, InvalidStrainException, Suits, Pass
from enum import Enum
from game.get_input import get_input_list
from bots.randombotuser import RandomBotUser
from game.interface import HumanUser, User

from itertools import chain

class InvalidDealerException(Exception):
    pass

class InvalidBidException(Exception):
    pass


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
    def start_of_auction_generator():
        return FullContract(None, None, None, False, True)

    @staticmethod
    def passout_generator():
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


class Record:
    def __init__(self, dealer: Players):
        self.__dealer = dealer
        self.__record: Dict[Players, List[Bids]] = {
            Players.NORTH: [],
            Players.EAST: [],
            Players.SOUTH: [],
            Players.WEST: []
        }
        self.__player_currently_bidding = dealer

    @staticmethod
    def __cycle_of_players(dealer: Players) -> List[Players]:
        return [dealer.determine_nth_player_to_the_right(i) for i in range(4)]

    @staticmethod
    def __is_complete(dealer: Players, record: Dict[Players, List[Bids]]) -> bool:
        if Record.__is_passout(record):
            return True

        lowest_common_bidding_round = min([len(record[player]) for player in Players.players()])
        if lowest_common_bidding_round == 0:
            return False

        index_of_last_player_to_bid = min([Record.__cycle_of_players(dealer).index(player) for player in Players.players() if len(record[player]) == lowest_common_bidding_round])
        players_to_check = [Record.__cycle_of_players(dealer)[i] for i in range(4) if i != index_of_last_player_to_bid]

        for player in players_to_check:
            if record[player][-1] != Bids.PASS:
                return False

        return True

    def is_complete(self) -> bool:
        return Record.__is_complete(self.dealer, self.record)

    def add_bid(self, bid: Bids) -> None:
        if self.is_complete():
            raise ValueError("Cannot add a bid as bidding is complete")

        current_contract = self.determine_current_contract()

        if bid not in Bids.all_legal_bids(self.__player_currently_bidding, current_contract):
            raise ValueError("Cannot add bid as it is not a legal bid")

        if not isinstance(bid, Bids):
            raise TypeError("bid must be of type Bids")
        self.__record[self.__player_currently_bidding].append(bid)
        self.__player_currently_bidding = self.__player_currently_bidding.next_player()

    @property
    def record(self) -> Dict[Players, List[Bids]]:
        return self.__record

    @property
    def dealer(self) -> Players:
        return self.__dealer

    @staticmethod
    def __is_passout(record: Dict[Players, List[Bids]]) -> bool:
        for player in Players:
            if len(record[player]) != 0:
                if record[player][0] != Bids.PASS:
                    return False
            else:
                return False
        return True

    def _determine_highest_bid_and_bidder(self) -> Tuple[Bids, Union[Players, None]]:
        if Record.__is_passout(self.__record):
            raise ValueError("Cannot determine the highest player for a passout")

        bids_so_far = [(bid.value, bid, player) for player, player_bids in self.__record.items() for bid in player_bids
                       if bid.value in Contracts.contracts()]

        if len(bids_so_far) == 0:
            return Bids.PASS, None

        # This sorts on bid.value (a Contract type)
        highest_contract, highest_bid, highest_bidder = max(bids_so_far)

        return highest_bid, highest_bidder

    def _determine_doubled_status(self, highest_bid: Bids) -> Doubles:
        zipped = list(
            chain.from_iterable(
                # We append [Bids.PASS] because it is possible that the last real bid
                # gets removed by zip if it does not have a companion
                zip(*[self.__record[player] + [Bids.PASS] for player in Record.__cycle_of_players(self.__dealer)])
            )
        )

        highest_bid_index = zipped.index(highest_bid)
        bids_after_highest_bid = zipped[highest_bid_index:]

        if Doubles.REDOUBLE in [bid.value for bid in bids_after_highest_bid]:
            return Doubles.REDOUBLE
        elif Doubles.DOUBLE in [bid.value for bid in bids_after_highest_bid]:
            return Doubles.DOUBLE
        else:
            return Doubles.NONE

    def _determine_declarer(self, highest_bid: Bids, highest_bidder: Players) -> Players:
        highest_bid_strain = highest_bid.value.determine_strain()
        bids_that_are_same_strain = [
            bid for bid in Bids.bids()
            if isinstance(bid.value, Contracts) and bid.value.determine_strain() == highest_bid_strain
        ]

        for bid in bids_that_are_same_strain:
            if bid in self.__record[highest_bidder]:
                return highest_bidder
            elif bid in self.__record[highest_bidder.partner()]:
                return highest_bidder.partner()

        raise ValueError("highest_bid not found")

    def determine_current_contract(self) -> FullContract:
        highest_bid, highest_bidder = self._determine_highest_bid_and_bidder()
        if highest_bid == Bids.PASS:
            return FullContract.start_of_auction_generator()

        doubled = self._determine_doubled_status(highest_bid)
        declarer = self._determine_declarer(highest_bid, highest_bidder)
        return FullContract(highest_bid.value, doubled, declarer, False)

    def determine_full_contract(self) -> FullContract:
        """ TODO THIS SHOULD BE COMBINED WITH determine_current_contract? """
        if not self.is_complete():
            raise ValueError("Cannot call determine_full_contract if the record is not complete!")

        if Record.__is_passout(self.__record):
            return FullContract.passout_generator()

        highest_bid, highest_bidder = self._determine_highest_bid_and_bidder()
        doubled = self._determine_doubled_status(highest_bid)
        declarer = self._determine_declarer(highest_bid, highest_bidder)

        return FullContract(highest_bid.value, doubled, declarer, False)

    def beautify_history(self) -> str:
        cycle = Record.__cycle_of_players(self.__dealer)

        zipped = list(
            chain.from_iterable(
                # zip won't work properly if the players have made a different number of bids, hence the placeholder
                zip(*[self.__record[player] + ['Placeholder'] for player in cycle])
            )
        )

        bids = [bid for bid in zipped if bid != 'Placeholder']

        res = ''
        for player in cycle:
            res = res + player.value.ljust(8)

        res = res + '\n'

        for i in range(len(bids)):
            res = res + str(bids[i].value.value.ljust(8))

            if i % 4 == 3:
                res = res + '\n'

        return res


def auction(users: Dict[Players, User], dealer: Players) -> Record:
    if not isinstance(dealer, Players):
        raise TypeError("dealer must be of enum Players")

    record = Record(dealer)
    current_bidder = dealer

    while not record.is_complete():
        print('<------------- NEW BID --------------->')
        print('The current bidder is ' + str(current_bidder))
        current_contract = record.determine_current_contract()
        legal_bids = Bids.all_legal_bids(current_bidder, current_contract)
        legal_bids_beaut = Bids.beautify_legal_bids(current_bidder, current_contract)
        print('Legal bids:')
        print(legal_bids_beaut)
        bid = users[current_bidder].make_bid(current_bidder, record, legal_bids)
        print('You bid: ' + str(bid))
        record.add_bid(bid)
        current_bidder = current_bidder.next_player()
        print('Record:')
        #print(str(record))
        print(record.beautify_history())

    return record


if __name__ == "__main__":
    users = {
        Players.NORTH: RandomBotUser(),
        Players.SOUTH: RandomBotUser(),
        Players.WEST: RandomBotUser(),
        Players.EAST: RandomBotUser()
    }

    record = auction(users, Players.NORTH)
    print(record.determine_full_contract())