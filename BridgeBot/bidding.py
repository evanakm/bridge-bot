from enums import contracts, Players, Strains, AuctionStatus, Doubles


class InvalidDealerException(Exception):
    pass


class Contract:
    def __init__(self):
        self.level = 0
        self.strain = Strains.NT
        self.doubled = Doubles.NONE
        self.declarer = None





class Auction:
    contract = {'level': 0,
                'strain': None,
                'doubled': None,
                'declarer': None}

    def __init__(self, dealer):
        self.dealer = dealer.upper()

        if not isinstance(dealer, Players):
            raise InvalidDealerException('Invalid dealer')

        self.record = {
            Players.NORTH: [],
            Players.EAST: [],
            Players.SOUTH: [],
            Players.WEST: []
        }

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

        self.player_index = Players.players().index(self.dealer)
        self.last_bidder_index = None

        # Not sure about the following line
        for player in Players.players():
            self.record[player].append("-")

        self.bid_index = -1
        self.doubled_by = None
        self.redoubled = False
        self.consecutive_passes = 0

    # For debugging purposes, easier to reset than to create a new Auction
    def reset(self):
        contract = Contract()

        self.player_index = players.index(self.dealer)
        self.last_bidder_index = None

        for i in range(self.player_index):
            self.record[players[i]].append("-")

        self.bid_index = -1
        self.doubled_by = None # Redundant with contract dictionary, but makes the logic below much cleaner.
        self.redoubled = False
        self.consecutive_passes = 0

    def __increment_player(self):
        self.player = self.player.next_player()

    def pass_bid(self):
        if self.bid_index == -1:
            if self.consecutive_passes == 3: # Passing out
                self.record[self.player].append(PASS)
                self.contract.strain = Strains.NT
                return AuctionStatus.DONE
            else:  # Passing before an opening bid
                self.record[self.player].append(PASS)
                self.__increment_player()
                return AuctionStatus.CONTINUE
        elif self.consecutive_passes != 2: # Passing but not finishing
            self.record[self.player].append(PASS)
            self.__increment_player()
            return AuctionStatus.CONTINUE
        else:  # Three passes in a row.
            if self.redoubled:
                self.contract.doubled = Doubles.DOUBLE_DOWN
            elif self.doubled_by:
                self.contract.doubled = Doubles.DOUBLE
            else:
                self.contract.doubled = Doubles.NONE

            self.contract.strain = strains[self.bid_index % 5]
            self.contract.level = int( 1 + (self.bid_index / 5) )

            # Kept track of who was the first to bid a strain
            if self.last_bidder_index % 2 == 0:
                self.contract.declarer = self.ns_first_bid[self.contract.strain]
            else:
                self.contract.declarer = self.ew_first_bid[self.contract.strain]

            self.record[self.player].append(PASS)
            return AuctionStatus.DONE

    def make_bid(self, bid_index):
        if bid_index not in range(35):
            return AuctionStatus.INVALID

        if bid_index <= self.bid_index:
            return AuctionStatus.INVALID

        self.bid_index = bid_index
        self.doubled_by = None
        self.redoubled = False
        self.consecutive_passes = 0

        self.record[self.player].append(contracts[bid_index])
        return AuctionStatus.CONTINUE

    def double(self):
        if self.bid_index == -1:  # No bids yet
            return AuctionStatus.INVALID
        elif self.redoubled:
            return AuctionStatus.INVALID
        elif self.player_index % 2 == 0 and self.doubled_by == "NS":  # Already doubled
            return AuctionStatus.INVALID
        elif self.player_index % 2 == 1 and self.doubled_by == "EW":  # Already doubled
            return AuctionStatus.INVALID
        elif self.last_bidder_index % 2 == self.player_index % 2:  # Can't double yourself
            return AuctionStatus.INVALID
        else:
            if self.player_index % 2 == 0:
                self.doubled_by = "NS"
                self.record[self.player].append(Doubles.DOUBLE)
                return AuctionStatus.CONTINUE
            else:
                self.doubled_by = "EW"
                self.record[self.player].append(Doubles.DOUBLE)
                return AuctionStatus.CONTINUE

    def redouble(self):
        if not self.doubled_by:  # Can't redouble unless first doubled
            return AuctionStatus.INVALID
        elif self.doubled_by == "NS" and self.player_index % 2 == 0:  # Can only redouble opponent's double
            return AuctionStatus.INVALID
        elif self.doubled_by == "EW" and self.player_index % 2 == 1:  # Can only redouble opponent's double
            return AuctionStatus.INVALID
        else:
            self.doubled_by = None
            self.redoubled = True
            self.record[players[self.player_index]].append(Doubles.DOUBLE_DOWN)
            return AuctionStatus.CONTINUE

