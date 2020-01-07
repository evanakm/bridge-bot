import pytest
import sys

sys.path.insert(0,'../bridgebot')
sys.path.insert(0,'..')

from contextlib import contextmanager
from bidding import Record
from game.enums import Players, Doubles, Contracts
from bidding import Bids, FullContract


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize('dealer, bids, expected', [
    (
            Players.EAST,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.PASS
            ],
            False
    ),
    (
            Players.WEST,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.PASS
            ],
            False
    ),
    (
            Players.NORTH,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.PASS
            ],
            False
    ),
    (
            Players.EAST,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.PASS,
                Bids.PASS
            ],
            True
    ),
    (
            Players.EAST,
            [
                Bids.FIVE_CLUBS,
                Bids.PASS,
                Bids.PASS,
                Bids.PASS
            ],
            True
    ),
    (
            Players.EAST,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.FIVE_CLUBS,
                Bids.PASS
            ],
            False
    ),
    (
            Players.EAST,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.FIVE_CLUBS,
                Bids.PASS,
                Bids.PASS,
            ],
            False
    ),
    (
            Players.EAST,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.FIVE_CLUBS,
                Bids.PASS,
                Bids.PASS,
                Bids.PASS
            ],
            True
    ),
])
def test_bidding(dealer, bids, expected):
    record = Record(dealer)
    for bid in bids:
        print(bid)
        record.add_bid(bid)
    print(expected)
    assert record.complete() == expected






@pytest.mark.parametrize('dealer, bids, expected', [
    (
            Players.EAST,
            [
                Bids.FIVE_CLUBS,
                Bids.PASS,
                Bids.PASS,
                Bids.PASS
            ],
            (Bids.FIVE_CLUBS, Players.EAST)
    ),
    (
            Players.EAST,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.FIVE_CLUBS,
                Bids.PASS,
                Bids.PASS,
                Bids.PASS
            ],
            (Bids.FIVE_CLUBS, Players.WEST)
    ),
    (
            Players.EAST,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.FIVE_CLUBS,
                Bids.PASS
            ],
            (Bids.FIVE_CLUBS, Players.WEST)
    ),
    (
            Players.EAST,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.FIVE_CLUBS,
                Bids.PASS,
                Bids.PASS,
            ],
            (Bids.FIVE_CLUBS, Players.WEST)
    ),
    (
            Players.EAST,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.FIVE_CLUBS,
                Bids.DOUBLE,
                Bids.PASS,
            ],
            (Bids.FIVE_CLUBS, Players.WEST)
    ),
    (
            Players.EAST,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.FIVE_CLUBS,
                Bids.DOUBLE,
                Bids.REDOUBLE,
                Bids.SIX_CLUBS
            ],
            (Bids.SIX_CLUBS, Players.SOUTH)
    ),
])
def test_determine_highest_bid_and_bidder(dealer, bids, expected):
    record = Record(dealer)
    for bid in bids:
        record.add_bid(bid)
    assert record._determine_highest_bid_and_bidder() == expected


@pytest.mark.parametrize('dealer, bids, expected', [
    (
            Players.EAST,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.PASS
            ],
            pytest.raises(ValueError)
    ),
    (
            Players.WEST,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.PASS
            ],
            pytest.raises(ValueError)
    ),
    (
            Players.NORTH,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.PASS
            ],
            pytest.raises(ValueError)
    ),
    (
            Players.EAST,
            [
                Bids.PASS,
                Bids.PASS,
                Bids.PASS,
                Bids.PASS
            ],
            pytest.raises(ValueError)
    ),
])
def test_determine_highest_bid_and_bidder_exceptions(dealer, bids, expected):
    record = Record(dealer)
    for bid in bids:
        print(bid)
        record.add_bid(bid)
    with expected:
        assert record._determine_highest_bid_and_bidder() == expected


@pytest.mark.parametrize('dealer, bids, expected', [
    (
            Players.EAST,
            [
                Bids.ONE_CLUB,
                Bids.TWO_CLUBS,
                Bids.THREE_CLUBS,
                Bids.FOUR_CLUBS,
                Bids.PASS,
                Bids.PASS,
                Bids.PASS
            ],
            Players.SOUTH
    ),
])
def test_determine_declarer(dealer, bids, expected):
    record = Record(dealer)
    for bid in bids:
        print(bid)
        record.add_bid(bid)
    highest_bid, highest_bidder = record._determine_highest_bid_and_bidder()
    assert record._determine_declarer(highest_bid, highest_bidder) == expected

@pytest.mark.parametrize('bid, bidder, current_contract, expected', [
    (Bids.ONE_NO_TRUMP, Players.NORTH, FullContract(Contracts.ONE_HEART, Doubles.NONE, Players.SOUTH), True),
])
def test_is_sufficient_bid(bid, bidder, current_contract, expected):
    assert Bids._is_sufficient_bid(bid, bidder, current_contract) == expected
