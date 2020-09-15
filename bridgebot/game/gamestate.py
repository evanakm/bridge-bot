from typing import Dict, List

from game.bids import Bids
from game.enums import Players, Contracts, ContractNotFound, Strains

from game.bridgehand import BridgeHand
from game.interface import User


class GameState:
    def __init__(self, users: Dict[Players, User], hands: Dict[Players, BridgeHand], contract: Contracts,
                 declarer: Players, bid_history: Dict[Players, List[Bids]]):
        if not isinstance(users, dict):
            raise TypeError("users is not of type dict")

        for key, val in users.items():
            if not isinstance(key, Players):
                raise TypeError("users key is not of type Players")

            if not isinstance(val, User):
                raise TypeError("users value is not of type User")

        if not isinstance(declarer, Players):
            raise TypeError("Invalid declarer")

        if not isinstance(contract, Contracts):
            raise ContractNotFound("Invalid Contract")

        self.users: Dict[Players, User] = users
        self.hands = hands
        self.__contract = contract
        self.__declarer = declarer
        self.__bid_history = bid_history
        self.card_history = {
            Players.NORTH: [],
            Players.EAST: [],
            Players.WEST: [],
            Players.SOUTH: []
        }

        self.leader_history: List[Players] = []

        self.ns_tricks = 0
        self.ew_tricks = 0

    @property
    def dummy(self) -> Players:
        return self.declarer.partner()

    @property
    def strain(self) -> Strains:
        return self.contract.determine_strain()

    @property
    def contract(self) -> Contracts:
        return self.__contract

    @property
    def declarer(self) -> Players:
        return self.__declarer

    @property
    def bid_history(self) -> Dict[Players, List[Bids]]:
        return self.__bid_history
