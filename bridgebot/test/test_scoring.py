import pytest
import sys

sys.path.insert(0,'../bridgebot')
sys.path.insert(0,'..')

from game.scoring import get_score_from_result
from game.enums import Contracts, Doubles

# Doing this as a black box test
@pytest.mark.parametrize('contract, doubled, tricks_taken, vulnerability, expected', [
    (Contracts.ONE_NO_TRUMP, Doubles.NONE, 8, False, 120),
    (Contracts.ONE_NO_TRUMP, Doubles.NONE, 8, True, 120),
    (Contracts.ONE_NO_TRUMP, Doubles.DOUBLE, 8, False, 280),
    (Contracts.ONE_NO_TRUMP, Doubles.DOUBLE, 8, True, 380),
    (Contracts.ONE_NO_TRUMP, Doubles.REDOUBLE, 8, False, 760),
    (Contracts.ONE_NO_TRUMP, Doubles.REDOUBLE, 8, True, 1160),
    (Contracts.THREE_NO_TRUMP, Doubles.NONE, 8, False, -50),
    (Contracts.THREE_NO_TRUMP, Doubles.NONE, 8, True, -100),
    (Contracts.TWO_NO_TRUMP, Doubles.DOUBLE, 8, False, 490),
    (Contracts.TWO_NO_TRUMP, Doubles.DOUBLE, 8, True, 690),
    (Contracts.TWO_NO_TRUMP, Doubles.REDOUBLE, 8, False, 680),
    (Contracts.TWO_NO_TRUMP, Doubles.REDOUBLE, 8, True, 880),
    (Contracts.THREE_NO_TRUMP, Doubles.DOUBLE, 8, False, -100),
    (Contracts.THREE_NO_TRUMP, Doubles.DOUBLE, 8, True, -200),
    (Contracts.FOUR_NO_TRUMP, Doubles.DOUBLE, 8, False, -300),
    (Contracts.FOUR_NO_TRUMP, Doubles.DOUBLE, 8, True, -500),
    (Contracts.FIVE_NO_TRUMP, Doubles.DOUBLE, 8, False, -500),
    (Contracts.FIVE_NO_TRUMP, Doubles.DOUBLE, 8, True, -800),
    (Contracts.SIX_NO_TRUMP, Doubles.DOUBLE, 8, False, -800),
    (Contracts.SIX_NO_TRUMP, Doubles.DOUBLE, 8, True, -1100),
    (Contracts.THREE_NO_TRUMP, Doubles.REDOUBLE, 8, False, -200),
    (Contracts.THREE_NO_TRUMP, Doubles.REDOUBLE, 8, True, -400),
    (Contracts.FOUR_NO_TRUMP, Doubles.REDOUBLE, 8, False, -600),
    (Contracts.FOUR_NO_TRUMP, Doubles.REDOUBLE, 8, True, -1000),
    (Contracts.FIVE_NO_TRUMP, Doubles.REDOUBLE, 8, False, -1000),
    (Contracts.FIVE_NO_TRUMP, Doubles.REDOUBLE, 8, True, -1600),
    (Contracts.SIX_NO_TRUMP, Doubles.REDOUBLE, 8, False, -1600),
    (Contracts.SIX_NO_TRUMP, Doubles.REDOUBLE, 8, True, -2200),
    (Contracts.ONE_NO_TRUMP, Doubles.NONE, 9, False, 150),
    (Contracts.ONE_NO_TRUMP, Doubles.NONE, 9, True, 150),
    (Contracts.ONE_NO_TRUMP, Doubles.DOUBLE, 9, False, 380),
    (Contracts.ONE_NO_TRUMP, Doubles.DOUBLE, 9, True, 580),
    (Contracts.ONE_NO_TRUMP, Doubles.REDOUBLE, 9, False, 960),
    (Contracts.ONE_NO_TRUMP, Doubles.REDOUBLE, 9, True, 1560),
    (Contracts.THREE_NO_TRUMP, Doubles.NONE, 9, False, 400),
    (Contracts.THREE_NO_TRUMP, Doubles.NONE, 9, True, 600),
    (Contracts.THREE_NO_TRUMP, Doubles.NONE, 10, False, 430),
    (Contracts.THREE_NO_TRUMP, Doubles.NONE, 10, True, 630),
    (Contracts.TWO_NO_TRUMP, Doubles.DOUBLE, 9, False, 590),
    (Contracts.TWO_NO_TRUMP, Doubles.DOUBLE, 9, True, 890),
    (Contracts.TWO_NO_TRUMP, Doubles.REDOUBLE, 9, False, 880),
    (Contracts.TWO_NO_TRUMP, Doubles.REDOUBLE, 9, True, 1280),
    (Contracts.SIX_NO_TRUMP, Doubles.NONE, 12, False, 990),
    (Contracts.SIX_NO_TRUMP, Doubles.NONE, 12, True, 1440),
    (Contracts.SIX_NO_TRUMP, Doubles.DOUBLE, 12, False, 1230),
    (Contracts.SIX_NO_TRUMP, Doubles.DOUBLE, 12, True, 1680),
    (Contracts.SIX_NO_TRUMP, Doubles.REDOUBLE, 12, False, 1660),
    (Contracts.SIX_NO_TRUMP, Doubles.REDOUBLE, 12, True, 2110),
    (Contracts.SIX_NO_TRUMP, Doubles.NONE, 13, False, 1020),
    (Contracts.SIX_NO_TRUMP, Doubles.NONE, 13, True, 1470),
    (Contracts.SIX_NO_TRUMP, Doubles.DOUBLE, 13, False, 1330),
    (Contracts.SIX_NO_TRUMP, Doubles.DOUBLE, 13, True, 1880),
    (Contracts.SIX_NO_TRUMP, Doubles.REDOUBLE, 13, False, 1860),
    (Contracts.SIX_NO_TRUMP, Doubles.REDOUBLE, 13, True, 2510),
    (Contracts.SEVEN_NO_TRUMP, Doubles.NONE, 13, False, 1520),
    (Contracts.SEVEN_NO_TRUMP, Doubles.NONE, 13, True, 2220),
    (Contracts.THREE_CLUBS, Doubles.NONE, 9, True, 110),
    (Contracts.THREE_CLUBS, Doubles.NONE, 11, True, 150),
    (Contracts.FIVE_CLUBS, Doubles.NONE, 11, False, 400),
    (Contracts.FIVE_CLUBS, Doubles.NONE, 11, True, 600),
    (Contracts.ONE_HEART, Doubles.NONE, 8, True, 110),
    (Contracts.ONE_HEART, Doubles.NONE, 10, True, 170),
    (Contracts.FOUR_HEARTS, Doubles.NONE, 10, False, 420),
    (Contracts.FOUR_HEARTS, Doubles.NONE, 11, True, 650),
])
def test_get_score_from_result(contract, doubled, tricks_taken, vulnerability, expected):
    score = get_score_from_result(contract, doubled, tricks_taken, vulnerability)
    print(score)
    assert score == expected