bids = ['1C',' 1D', '1H', '1S', '1N',
        '2C', '2D', '2H', '2S', '2N',
        '3C', '3D', '3H', '3S', '3N',
        '4C', '4D', '4H', '4S', '4N',
        '5C', '5D', '5H', '5S', '5N',
        '6C', '6D', '6H', '6S', '6N',
        '7C', '7D', '7H', '7S', '7N']

players = ['NORTH', 'EAST', 'SOUTH', 'WEST']

strains = ['CLUBS', 'DIAMONDS', 'HEARTS', 'SPADES', 'NT', 'PASSOUT']

doubles = [None, 'X', 'XX']

ps = 'PASS'


class Auction:
    contract = {'level': 0,
                'strain': None,
                'doubled': None,
                'declarer': None}

    def __init__(self, dealer):
        self.dealer = dealer.upper()

        if not dealer in players:
            raise Exception('Invalid dealer.')

        self.record = {
            'NORTH': [],
            'EAST': [],
            'SOUTH': [],
            'WEST': []
        }

        self.ns_first_bid = {
            'CLUBS':"",
            'DIAMONDS':"",
            'HEARTS':"",
            'SPADES':"",
            'NT':""
        }

        self.ew_first_bid = {
            'CLUBS': "",
            'DIAMONDS': "",
            'HEARTS': "",
            'SPADES': "",
            'NT': ""
        }

        self.player_index = players.index(self.dealer)
        self.last_bidder_index = None

        for i in range(self.player_index):
            self.record[players[i]].append("-")

        self.bid_index = -1
        self.doubled_by = None
        self.redoubled = False
        self.consecutive_passes = 0

    # For debugging purposes, easier to reset than to create a new Auction
    def reset(self):
        contract = {'level': 0,
                    'strain': None,
                    'doubled': None,
                    'declarer': None}

        self.player_index = players.index(self.dealer)
        self.last_bidder_index = None

        for i in range(self.player_index):
            self.record[players[i]].append("-")

        self.bid_index = -1
        self.doubled_by = None # Redundant with contract dictionary, but makes the logic below much cleaner.
        self.redoubled = False
        self.consecutive_passes = 0

    def __increment_player(self):
        self.player_index = (self.player_index + 1) % 4

    # Bids return either "DONE" or "CONTINUE" depending on whether the auction is finished,
    # or "INVALID" if the bid is not allowed.
    ret_val = ["DONE", "CONTINUE", "INVALID"]

    def pass_bid(self):
        if self.bid_index == -1:
            if self.consecutive_passes == 3: # Passing out
                self.record[players[self.player_index]].append(ps)
                self.contract['strain'] = strains[5]
                return self.ret_val[0]
            else:  # Passing before an opening bid
                self.record[players[self.player_index]].append(ps)
                self.__increment_player()
                return self.ret_val[1]  # "CONTINUE"
        elif self.consecutive_passes != 2: # Passing but not finishing
            self.record[players[self.player_index]].append(ps)
            self.__increment_player()
            return self.ret_val[1]  # "CONTINUE"
        else:  # Three passes in a row.
            if self.redoubled:
                self.contract['doubled'] = doubles[2]
            elif self.doubled_by:
                self.contract['doubled'] = doubles[1]
            else:
                self.contract['doubled'] = doubles[0]

            self.contract['strain'] = strains[self.bid_index % 5]
            self.contract['level'] = int( 1 + (self.bid_index / 5) )

            # Kept track of who was the first to bid a strain
            if self.last_bidder_index % 2 == 0:
                self.contract['declarer'] = self.ns_first_bid[self.contract['strain']]
            else:
                self.contract['declarer'] = self.ew_first_bid[self.contract['strain']]

            self.record[players[self.player_index]].append(ps)
            return self.ret_val[0]  # "DONE"

    def make_bid(self,bid_index):
        if bid_index not in range(35):
            return self.ret_val[2]  # "INVALID"

        if bid_index <= self.bid_index:
            return self.ret_val[2]  # "INVALID"

        self.bid_index = bid_index
        self.doubled_by = None
        self.redoubled = False
        self.consecutive_passes = 0

        self.record[players[self.player_index]].append(bids[bid_index])
        return self.ret_val[1]  # "CONTINUE"

    def double(self):
        if self.bid_index == -1:  # No bids yet
            return self.ret_val[2]  # "INVALID"
        elif self.redoubled:
            return self.ret_val[2]  # "INVALID"
        elif self.player_index % 2 == 0 and self.doubled_by == "NS":  # Already doubled
            return self.ret_val[2]  # "INVALID"
        elif self.player_index % 2 == 1 and self.doubled_by == "EW":  # Already doubled
            return self.ret_val[2]  # "INVALID"
        elif self.last_bidder_index % 2 == self.player_index % 2:  # Can't double yourself
            return self.ret_val[2]  # "INVALID"
        else:
            if self.player_index % 2 == 0:
                self.doubled_by = "NS"
                self.record[players[self.player_index]].append(doubles[1])
                return self.ret_val[1]  # "CONTINUE"
            else:
                self.doubled_by = "EW"
                self.record[players[self.player_index]].append(doubles[1])
                return self.ret_val[1]  # "CONTINUE"

    def redouble(self):
        if not self.doubled_by:  # Can't redouble unless first doubled
            return self.ret_val[2]  # "INVALID"
        elif self.doubled_by == "NS" and self.player_index % 2 == 0:  # Can only redouble opponent's double
            return self.ret_val[2]  # "INVALID"
        elif self.doubled_by == "EW" and self.player_index % 2 == 1:  # Can only redouble opponent's double
            return self.ret_val[2]  # "INVALID"
        else:
            self.doubled_by = None
            self.redoubled = True
            self.record[players[self.player_index]].append(doubles[2])
            return self.ret_val[1]  # "CONTINUE"

