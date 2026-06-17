import pytest

from bridgebot.bidding import Auction, Bids, FullContract, InvalidBidException
from bridgebot.game.enums import AuctionStatus, Contracts, Doubles, Players


def current_one_club_by_east():
    return FullContract(Contracts.ONE_CLUB, Doubles.NONE, Players.EAST, False)


def test_higher_contract_bid_is_sufficient():
    assert Bids.is_sufficient_bid(
        Bids.TWO_CLUBS,
        Players.NORTH,
        current_one_club_by_east(),
    ) is True


def test_lower_contract_bid_is_not_sufficient():
    current_contract = FullContract(
        Contracts.TWO_CLUBS,
        Doubles.NONE,
        Players.EAST,
        False,
    )

    assert Bids.is_sufficient_bid(
        Bids.ONE_CLUB,
        Players.NORTH,
        current_contract,
    ) is False


def test_all_legal_bids_includes_raise_and_opponent_double():
    legal_bids = Bids.all_legal_bids(Players.NORTH, current_one_club_by_east())

    assert Bids.ONE_CLUB not in legal_bids
    assert Bids.TWO_CLUBS in legal_bids
    assert Bids.DOUBLE in legal_bids


def test_all_legal_bids_after_double_allows_redouble_by_doubled_side():
    current_contract = FullContract(
        Contracts.ONE_HEART,
        Doubles.DOUBLE,
        Players.NORTH,
        False,
    )

    legal_bids = Bids.all_legal_bids(Players.SOUTH, current_contract)

    assert Bids.REDOUBLE in legal_bids
    assert Bids.DOUBLE not in legal_bids


def test_all_legal_bids_after_double_rejects_opponent_redouble():
    current_contract = FullContract(
        Contracts.ONE_HEART,
        Doubles.DOUBLE,
        Players.NORTH,
        False,
    )

    legal_bids = Bids.all_legal_bids(Players.WEST, current_contract)

    assert Bids.REDOUBLE not in legal_bids
    assert Bids.DOUBLE not in legal_bids


def test_auction_can_be_created_for_a_dealer():
    auction = Auction(Players.NORTH)

    assert auction.dealer == Players.NORTH
    assert auction.record.dealer == Players.NORTH


def test_auction_passout_finishes_with_passout_contract():
    auction = Auction(Players.NORTH)

    assert auction.get_new_bid(Bids.PASS) == AuctionStatus.CONTINUE
    assert auction.get_new_bid(Bids.PASS) == AuctionStatus.CONTINUE
    assert auction.get_new_bid(Bids.PASS) == AuctionStatus.CONTINUE
    assert auction.get_new_bid(Bids.PASS) == AuctionStatus.DONE

    contract = auction.determine_full_contract()
    assert contract.passout is True
    assert contract.contract is None


def test_auction_tracks_final_contract_doubled_status_and_declarer():
    auction = Auction(Players.NORTH)

    bids = [
        Bids.ONE_HEART,
        Bids.DOUBLE,
        Bids.REDOUBLE,
        Bids.PASS,
        Bids.FOUR_HEARTS,
        Bids.PASS,
        Bids.PASS,
        Bids.PASS,
    ]

    for bid in bids[:-1]:
        assert auction.get_new_bid(bid) == AuctionStatus.CONTINUE
    assert auction.get_new_bid(bids[-1]) == AuctionStatus.DONE

    contract = auction.determine_full_contract()
    assert contract.passout is False
    assert contract.contract == Contracts.FOUR_HEARTS
    assert contract.doubled == Doubles.NONE
    assert contract.declarer == Players.NORTH


def test_auction_tracks_final_doubled_contract():
    auction = Auction(Players.NORTH)

    bids = [
        Bids.ONE_HEART,
        Bids.DOUBLE,
        Bids.PASS,
        Bids.PASS,
        Bids.PASS,
    ]

    for bid in bids[:-1]:
        assert auction.get_new_bid(bid) == AuctionStatus.CONTINUE
    assert auction.get_new_bid(bids[-1]) == AuctionStatus.DONE

    contract = auction.determine_full_contract()
    assert contract.contract == Contracts.ONE_HEART
    assert contract.doubled == Doubles.DOUBLE
    assert contract.declarer == Players.NORTH


def test_auction_tracks_final_redoubled_contract():
    auction = Auction(Players.NORTH)

    bids = [
        Bids.ONE_HEART,
        Bids.DOUBLE,
        Bids.REDOUBLE,
        Bids.PASS,
        Bids.PASS,
        Bids.PASS,
    ]

    for bid in bids[:-1]:
        assert auction.get_new_bid(bid) == AuctionStatus.CONTINUE
    assert auction.get_new_bid(bids[-1]) == AuctionStatus.DONE

    contract = auction.determine_full_contract()
    assert contract.contract == Contracts.ONE_HEART
    assert contract.doubled == Doubles.REDOUBLE
    assert contract.declarer == Players.NORTH


def test_record_rejects_double_before_opening_bid():
    auction = Auction(Players.NORTH)

    with pytest.raises(InvalidBidException):
        auction.get_new_bid(Bids.DOUBLE)


def test_auction_rotates_from_dealer_clockwise():
    auction = Auction(Players.EAST)

    assert auction.player == Players.EAST
    assert auction.get_new_bid(Bids.PASS) == AuctionStatus.CONTINUE
    assert auction.player == Players.SOUTH
    assert auction.get_new_bid(Bids.PASS) == AuctionStatus.CONTINUE
    assert auction.player == Players.WEST
    assert auction.get_new_bid(Bids.PASS) == AuctionStatus.CONTINUE
    assert auction.player == Players.NORTH
    assert auction.get_new_bid(Bids.PASS) == AuctionStatus.DONE


def test_auction_allows_balancing_double_after_two_passes():
    auction = Auction(Players.NORTH)
    bids = [
        Bids.ONE_HEART,
        Bids.PASS,
        Bids.PASS,
        Bids.DOUBLE,
        Bids.PASS,
        Bids.PASS,
        Bids.PASS,
    ]

    for bid in bids[:-1]:
        assert auction.get_new_bid(bid) == AuctionStatus.CONTINUE
    assert auction.get_new_bid(bids[-1]) == AuctionStatus.DONE

    contract = auction.determine_full_contract()
    assert contract.contract == Contracts.ONE_HEART
    assert contract.doubled == Doubles.DOUBLE
    assert contract.declarer == Players.NORTH


def test_new_contract_bid_resets_previous_double_and_redouble():
    auction = Auction(Players.NORTH)
    for bid in [
        Bids.ONE_HEART,
        Bids.DOUBLE,
        Bids.REDOUBLE,
        Bids.TWO_CLUBS,
    ]:
        assert auction.get_new_bid(bid) == AuctionStatus.CONTINUE

    assert Bids.DOUBLE in auction.legal_bids()
    assert Bids.REDOUBLE not in auction.legal_bids()

    for bid in [Bids.DOUBLE, Bids.PASS, Bids.PASS]:
        assert auction.get_new_bid(bid) == AuctionStatus.CONTINUE
    assert auction.get_new_bid(Bids.PASS) == AuctionStatus.DONE

    contract = auction.determine_full_contract()
    assert contract.contract == Contracts.TWO_CLUBS
    assert contract.doubled == Doubles.DOUBLE
    assert contract.declarer == Players.WEST


def test_declarer_is_first_partnership_player_to_bid_final_strain():
    auction = Auction(Players.NORTH)
    bids = [
        Bids.ONE_HEART,
        Bids.PASS,
        Bids.FOUR_HEARTS,
        Bids.PASS,
        Bids.PASS,
        Bids.PASS,
    ]

    for bid in bids[:-1]:
        assert auction.get_new_bid(bid) == AuctionStatus.CONTINUE
    assert auction.get_new_bid(bids[-1]) == AuctionStatus.DONE

    contract = auction.determine_full_contract()
    assert contract.contract == Contracts.FOUR_HEARTS
    assert contract.declarer == Players.NORTH
