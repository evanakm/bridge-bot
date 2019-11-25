import pytest
import sys

sys.path.insert(0,'../bridgebot')
sys.path.insert(0,'..')

from contextlib import contextmanager
from bidding import Record
from game.enums import Players
from bidding import Bids


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
        record.add_bid(bid)
    print(expected)
    assert record.complete() == expected
