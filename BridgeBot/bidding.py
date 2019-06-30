from cards import suits

bids = ['1C',' 1D', '1H', '1S', '1N',
        '2C', '2D', '2H', '2S', '2N',
        '3C', '3D', '3H', '3S', '3N',
        '4C', '4D', '4H', '4S', '4N',
        '5C', '5D', '5H', '5S', '5N',
        '6C', '6D', '6H', '6S', '6N',
        '7C', '7D', '7H', '7S', '7N']

calls = ['PASS','X','XX']

players = ['NORTH', 'EAST', 'SOUTH', 'WEST']


class Auction:
    def __init__(self, dealer):
        dealer = dealer.upper()

        if not dealer in players:
            raise Exception('Invalid dealer.')

        self.record = {
            'NORTH':[],
            'EAST':[],
            'SOUTH':[],
            'WEST':[]
        }

        self.ns_first_bid = {
            'CLUBS':"",
            'DIAMONDS':"",
            'HEARTS':"",
            'SPADES':"",
            'NT':""
        }

        self.ew_first_bid = {
            'CLUBS':"",
            'DIAMONDS':"",
            'HEARTS':"",
            'SPADES':"",
            'NT':""
        }

        self.player_index = players.index(dealer)
        self.last_bidder_index = None

        for i in range(self.player_index):
            self.record[players[i]].append("-")

        self.bid_index = -1
        self.doubled_by = None
        self.redoubled = False
        self.consecutive_passes = 0

    def __increment_player(self):
        self.player_index = (self.player_index + 1) % 4

    def pass_bid(self):
        if self.bid_index == -1:
            if self.consecutive_passes == 3:
                self.record[players[self.player_index]].append(calls[0])
                return "PASSOUT"
            else:
                self.record[players[self.player_index]].append(calls[0])
                self.__increment_player()
                return "CONTINUE"
        elif self.consecutive_passes != 2:
            self.record[players[self.player_index]].append(calls[0])
            self.__increment_player()
            return "CONTINUE"
        else:
            if self.redoubled:
                contract = " " + calls[2]
            elif self.doubled_by:
                contract = " " + calls[1]
            else:
                contract = ""

            contract = "CONTRACT: " + bids[self.bid_index] + contract

            declarer = " BY "

            if self.bid_index % 5 == 0:
                if self.last_bidder_index % 2 == 0:
                    declarer = declarer + self.ns_first_bid["CLUBS"]
                else:
                    declarer = declarer + self.ew_first_bid["CLUBS"]
            elif self.bid_index % 5 == 1:
                if self.last_bidder_index % 2 == 0:
                    declarer = declarer + self.ns_first_bid["DIAMONDS"]
                else:
                    declarer = declarer + self.ew_first_bid["DIAMONDS"]
            elif self.bid_index % 5 == 2:
                if self.last_bidder_index % 2 == 0:
                    declarer = declarer + self.ns_first_bid["HEARTS"]
                else:
                    declarer = declarer + self.ew_first_bid["HEARTS"]
            elif self.bid_index % 5 == 3:
                if self.last_bidder_index % 2 == 0:
                    declarer = declarer + self.ns_first_bid["SPADES"]
                else:
                    declarer = declarer + self.ew_first_bid["SPADES"]
            elif self.bid_index % 5 == 4:
                if self.last_bidder_index % 2 == 0:
                    declarer = declarer + self.ns_first_bid["NT"]
                else:
                    declarer = declarer + self.ew_first_bid["NT"]

            self.record[players[self.player_index]].append(calls[0])
            return contract + declarer

    def make_bid(self,bid_index):
        if not bid_index in range(35):
            raise Exception("Invalid bid index.")

        if bid_index <= self.bid_index:
            return "INSUFFICIENT"

        self.bid_index = bid_index
        self.doubled_by = None
        self.redoubled = False
        self.consecutive_passes = 0

        self.record[players[self.player_index]].append(bids[bid_index])
        return "CONTINUE"

    def double(self):
        if self.bid_index == -1: #No bids yet
            return "INSUFFICIENT"
        elif self.redoubled:
            return "INSUFFICIENT"
        elif self.player_index % 2 == 0 and self.doubled_by == "NS": #Already doubled
            return "INSUFFICIENT"
        elif self.player_index % 2 == 1 and self.doubled_by == "EW": #Already doubled
            return "INSUFFICIENT"
        elif self.last_bidder_index % 2 == self.player_index % 2: #Can't double yourself
            return "INSUFFICIENT"
        else:
            if self.player_index % 2 == 0:
                self.doubled_by = "NS"
                self.record[players[self.player_index]].append(calls[1])
                return "CONTINUE"
            else:
                self.doubled_by = "EW"
                self.record[players[self.player_index]].append(calls[1])
                return "CONTINUE"

    def redouble(self):
        if not self.doubled_by: #Can't redouble unless first doubled
            return "INSUFFICIENT"
        elif self.doubled_by == "NS" and self.player_index % 2 == 0: #Can only redouble opponent's bid
            return "INSUFFICIENT"
        elif self.doubled_by == "EW" and self.player_index % 2 == 1: #Can only redouble opponent's bid
            return "INSUFFICIENT"
        else:
            self.doubled_by = None
            self.redoubled = True
            self.record[players[self.player_index]].append(calls[2])
            return "CONTINUE"

