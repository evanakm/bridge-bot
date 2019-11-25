from game.enums import Players, Strains, AuctionStatus, Doubles, Contracts, Team, InvalidPlayerException, InvalidStrainException, Suits
from enum import Enum

class InvalidDealerException(Exception):
    pass

class InvalidBidException(Exception):
    pass

class FullContract:
    def __init__(self, contract, doubled, declarer, passout):
        self.contract = contract
        self.doubled = doubled
        self.declarer = declarer
        self.passout = passout

        if not isinstance(passout, bool):
            raise TypeError("passout must be of type bool")

        if passout:
            return

        if not isinstance(contract, Contracts):
            raise TypeError("contract must be of enum Contracts")
        if not isinstance(doubled, Doubles):
            raise TypeError("doubled must be of enum Doubles")
        if not isinstance(declarer, Players):
            raise TypeError("declarer must be of type Players")


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
    PASS = "PASS"
    DOUBLE = Doubles.DOUBLE
    REDOUBLE = Doubles.REDOUBLE

    @staticmethod
    def bids():
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
    def is_sufficient_bid(bid, bidder, current_contract):
        if not isinstance(bidder, Players):
            raise Exception("by_bidder must be a Player")

        if not isinstance(current_contract, FullContract):
            raise Exception("Must compare to a Contract")

        if current_contract.contract is None:
            return bid != Bids.DOUBLE and bid != Bids.REDOUBLE

        if bid == Bids.PASS:
            return True

        if isinstance(bid, Contracts):
            return current_contract.contract < bid

        if bid == Bids.DOUBLE:
            if current_contract.contract is None:
                # Can't double until bidding has been opened
                return False
            elif current_contract.doubled != Doubles.NONE:
                # Can only double an undoubled contract
                return False
            elif Team.player_to_team(current_contract.declarer) == Team.player_to_team(bidder):
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

    def map_to_contract(self):
        bids = self.bids()
        return Contracts.contracts()[bids.index(self)]

    @staticmethod
    def all_legal_bids(bidder, current_contract):
        return [bid for bid in Bids.bids() if Bids.is_sufficent_bid(bid, bidder, current_contract)]


class Record:
    def __init__(self, dealer):
        self.__dealer = dealer
        self.__record = {
            Players.NORTH: [],
            Players.EAST: [],
            Players.SOUTH: [],
            Players.WEST: []
        }
        self.__player_currently_bidding = dealer

    @staticmethod
    def __complete(dealer, record):
        if Record.__is_passout(record):
            return True

        lowest_common_bidding_round = min([len(record[player]) for player in Players.players()])
        if lowest_common_bidding_round == 0:
            return False

        cycle_of_players = [dealer.determine_nth_player_to_the_right(i) for i in range(4)]
        index_of_last_player_to_bid = min([cycle_of_players.index(player) for player in Players.players() if len(record[player]) == lowest_common_bidding_round])
        players_to_check = [cycle_of_players[i] for i in range(4) if i != index_of_last_player_to_bid]

        for player in players_to_check:
            if record[player][-1] != Bids.PASS:
                return False

        return True


    def complete(self):
        is_complete = Record.__complete(self.dealer, self.record)

        # This is a side effect but I think it makes sense
        self.__player_currently_bidding = None

        return is_complete

    def add_bid(self, bid):
        """

        Parameters
        ----------
        player Players
        bid

        Returns
        -------

        """
        if not isinstance(bid, Bids):
            raise TypeError("bid must be of type Bids")
        self.__record[self.__player_currently_bidding].append(bid)
        self.__player_currently_bidding = self.__player_currently_bidding.next_player()

    @property
    def record(self):
        return self.__record

    @property
    def dealer(self):
        return self.__dealer

    @staticmethod
    def __is_passout(record):
        for player in Players:
            if len(record[player]) != 0:
                if record[player][0] != Bids.PASS:
                    return False
            else:
                return False
        return True

    def determine_full_contract(self):
        # TODO consider making this algorithm faster with memoization
        if Record.__is_passout(self.__record):
            return FullContract(None, None, None, True)
        player_to_check = self.__dealer
        most_recent_bid = None
        most_recent_doubler = Doubles.NONE

        first_ns_to_bid_strain = {
            Strains.CLUBS: None,
            Strains.DIAMONDS: None,
            Strains.HEARTS: None,
            Strains.SPADES: None,
            Strains.NT: None
        }

        first_ew_to_bid_strain = {
            Strains.CLUBS: None,
            Strains.DIAMONDS: None,
            Strains.HEARTS: None,
            Strains.SPADES: None,
            Strains.NT: None
        }

        bidding_round = 0

        pass_count = 0

        # Recall that in this function, we already check to see if it is a passout with the __is_passout function
        while True:
            if len(self.__record[player_to_check]) > bidding_round:
                if self.__record[player_to_check][bidding_round] == Bids.PASS:
                    pass_count += 1
                else:
                    pass_count = 0


    def try_to_set_first_bid(self, player, strain):
        if not isinstance(player, Players):
            raise InvalidPlayerException

        if not isinstance(strain, Strains):
            raise InvalidStrainException

        team = Team.player_to_team(player)

        if self.first_bids[team][strain] is None:
            # This is the ONLY case in which to do something. Otherwise do nothing.
            self.first_bids[team][strain] = player

    def get_first_bid(self, player, strain):
        team = Team.player_to_team(player)
        return self.first_bids[team][strain]


class Auction:
    def __init__(self, dealer):
        if not isinstance(dealer, Players):
            raise InvalidDealerException('Invalid dealer')

        self.dealer = dealer

        self.reset()

    # For debugging purposes, easier to reset than to create a new Auction
    def reset(self):
        self.player_index = Players.players().index(self.dealer)
        self.last_bidder_index = None
        self.record = Record(self.dealer)
        self.last_bid = None
        self.redoubled = False
        self.consecutive_passes = 0

        self.contract = FullContract()

    def __increment_player(self):
        self.player = self.player.next_player()

    def get_new_bid(self, new_bid):
        if not isinstance(new_bid, Bids):
            raise InvalidBidException("Not a valid bid.")
        if not new_bid.is_sufficient_bid(self.player, self.contract):
            raise InvalidBidException("Insufficient bid.")

        self.record[self.player].append(new_bid)

        if new_bid == Bids.PASS:
            if self.contract.contract is None:
                if self.consecutive_passes == 3:  # Passing out
                    return AuctionStatus.DONE
                else:  # Passing before an opening bid
                    self.__increment_player()
                    return AuctionStatus.CONTINUE
            elif self.consecutive_passes != 2:  # Passing but not finishing
                self.__increment_player()
                return AuctionStatus.CONTINUE
            else:  # Three passes in a row after at least one bid. Auction over.
                return AuctionStatus.DONE
        elif isinstance(new_bid, Contracts):
            self.contract.contract = new_bid.map_to_contract()
            self.contract.doubled = Doubles.NONE
            self.contract.last_bid_by = self.player

            # The logic behind finding self.contract.declarer is encapsulated in self.record
            strain = Strains.get_strain_from_contract(self.contract.contract)
            self.record.try_to_set_first_bid(self.player, strain)
            self.contract.declarer = self.record.get_first_bid(self.player, strain)

            self.consecutive_passes = 0

            return AuctionStatus.CONTINUE
        elif new_bid == Bids.DOUBLE:
            self.consecutive_passes = 0
            return AuctionStatus.CONTINUE
        elif new_bid == Bids.REDOUBLE:
            self.consecutive_passes = 0
            return AuctionStatus.CONTINUE

