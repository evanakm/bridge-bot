from enums import Players, Strains, AuctionStatus, Doubles, Contracts, PASS, Team


class InvalidDealerException(Exception):
    pass


class Contract:
    def __init__(self):
        self.level = 0
        self.strain = Strains.PASSOUT
        self.doubled = Doubles.NONE
        self.declarer = None


class Record:
    def __init__(self, first_bidder):
        self.first_bidder = first_bidder

        self.record = {
            Players.NORTH: [],
            Players.EAST: [],
            Players.SOUTH: [],
            Players.WEST: []
        }

    def __ns_first_bid(self, strain):
        return
        self.ns_first_bid = {
            Strains.CLUBS: None,
            Strains.DIAMONDS: None,
            Strains.HEARTS: None,
            Strains.SPADES: None,
            Strains.NT: None
        }

        self.ew_first_bid = {
            Strains.CLUBS: None,
            Strains.DIAMONDS: None,
            Strains.HEARTS: None,
            Strains.SPADES: None,
            Strains.NT: None
        }


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

        # Not sure about the following line
        for player in Players.players():
            self.record[player].append("-")

        self.last_bid = None
        self.doubled_by = None # Redundant with contract dictionary, but makes the logic below much cleaner.
        self.redoubled = False
        self.consecutive_passes = 0

        self.contract = Contract()

    def __increment_player(self):
        self.player = self.player.next_player()

    def pass_bid(self):
        if self.last_bid is None:
            if self.consecutive_passes == 3:  # Passing out
                self.record[self.player].append("PASS")
                self.contract.strain = Strains.PASSOUT
                return AuctionStatus.DONE
            else:  # Passing before an opening bid
                self.record[self.player].append("PASS")
                self.__increment_player()
                return AuctionStatus.CONTINUE
        elif self.consecutive_passes != 2:  # Passing but not finishing
            self.record[self.player].append("PASS")
            self.__increment_player()
            return AuctionStatus.CONTINUE
        else:  # Three passes in a row.
            if self.redoubled:
                self.contract.doubled = Doubles.REDOUBLE
            elif self.doubled_by:
                self.contract.doubled = Doubles.DOUBLE
            else:
                self.contract.doubled = Doubles.NONE

            self.contract.strain = Contracts.determine_strain_from_contract(self.bid)
            self.contract.level = Contracts.determine_level_from_contract(self.bid)

            # Kept track of who was the first to bid a strain
            if self.last_bidder_index % 2 == 0:
                self.contract.declarer = self.ns_first_bid[self.contract.strain]
            else:
                self.contract.declarer = self.ew_first_bid[self.contract.strain]

            self.record[self.player].append("PASS")
            return AuctionStatus.DONE

    def make_bid(self, bid):

        if not isinstance(bid, Contracts):
            return AuctionStatus.INVALID

        if bid <= self.last_bid:
            return AuctionStatus.INVALID

        self.last_bid = bid
        self.doubled_by = None
        self.redoubled = False
        self.consecutive_passes = 0

        self.record[self.player].append(bid)
        return AuctionStatus.CONTINUE

    def double(self):
        if self.bid_index == -1:  # No bids yet
            return AuctionStatus.INVALID
        elif self.redoubled:
            return AuctionStatus.INVALID
        elif self.player_index % 2 == 0 and self.doubled_by == Team.NS:  # Already doubled
            return AuctionStatus.INVALID
        elif self.player_index % 2 == 1 and self.doubled_by == Team.EW:  # Already doubled
            return AuctionStatus.INVALID
        elif self.last_bidder_index % 2 == self.player_index % 2:  # Can't double yourself
            return AuctionStatus.INVALID
        else:
            if self.player_index % 2 == 0:
                self.doubled_by = Team.NS
                self.record[self.player].append(Doubles.DOUBLE)
                return AuctionStatus.CONTINUE
            else:
                self.doubled_by = Team.EW
                self.record[self.player].append(Doubles.DOUBLE)
                return AuctionStatus.CONTINUE

    def redouble(self):
        if not self.doubled_by:  # Can't redouble unless first doubled
            return AuctionStatus.INVALID
        elif self.doubled_by == Team.NS and self.player_index % 2 == 0:  # Can only redouble opponent's double
            return AuctionStatus.INVALID
        elif self.doubled_by == Team.EW and self.player_index % 2 == 1:  # Can only redouble opponent's double
            return AuctionStatus.INVALID
        else:
            self.doubled_by = None
            self.redoubled = True
            self.record[Players.players()[self.player_index]].append(Doubles.REDOUBLE)
            return AuctionStatus.CONTINUE

