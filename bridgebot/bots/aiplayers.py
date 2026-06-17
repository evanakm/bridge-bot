import random
from collections import Counter

from bridgebot.bidding import Bids
from bridgebot.game.card import Card
from bridgebot.game.enums import Contracts, Players, Ranks, Strains, Suits
from bridgebot.game.interface import User


HONOR_POINTS = {
    Ranks.ACE: 4,
    Ranks.KING: 3,
    Ranks.QUEEN: 2,
    Ranks.JACK: 1,
}

STRAIN_PRIORITY = [
    Strains.SPADES,
    Strains.HEARTS,
    Strains.DIAMONDS,
    Strains.CLUBS,
    Strains.NT,
]


def high_card_points(cards):
    return sum(HONOR_POINTS.get(card.rank, 0) for card in cards)


def suit_lengths(cards):
    return {
        suit: len([card for card in cards if card.suit == suit])
        for suit in Suits.suits()
    }


def is_balanced(cards):
    lengths = sorted(suit_lengths(cards).values(), reverse=True)
    return lengths in ([4, 3, 3, 3], [4, 4, 3, 2], [5, 3, 3, 2])


def choose_bid_for_user(user, current_player, hand, legal_bids, bid_history):
    if hasattr(user, "bid_with_hand"):
        return user.bid_with_hand(current_player, hand, legal_bids, bid_history)
    return user.bid(current_player, legal_bids, bid_history)


def pass_bid(legal_bids):
    return Bids.PASS if Bids.PASS in legal_bids else legal_bids[0]


def contract_bid(level, strain):
    for bid in Bids.bids():
        if isinstance(bid.value, Contracts):
            if bid.value.determine_level() == level and bid.value.determine_strain() == strain:
                return bid
    return None


def opening_strain(cards):
    lengths = suit_lengths(cards)
    return max(
        STRAIN_PRIORITY[:-1],
        key=lambda strain: (lengths[strain.determine_suit()], -STRAIN_PRIORITY.index(strain)),
    )


def legal_contracts(legal_bids):
    return [bid for bid in legal_bids if isinstance(bid.value, Contracts)]


def infer_contract_strain(bid_history):
    if bid_history is None:
        return None
    try:
        full_contract = bid_history.determine_full_contract()
        if full_contract.passout or full_contract.contract is None:
            return None
        return full_contract.contract.determine_strain()
    except Exception:
        current_contract = getattr(bid_history, "current_contract", None)
        contract = getattr(current_contract, "contract", None)
        if contract is None:
            return None
        return contract.determine_strain()


def current_trick(current_player, card_history, leader_history):
    if not leader_history:
        return []

    leader = leader_history[-1]
    player = leader
    trick = []
    while player != current_player:
        played_cards = card_history.get(player, [])
        if played_cards:
            trick.append((player, played_cards[-1]))
        player = player.next_player()
    return trick


def card_rank_index(card):
    return Ranks.ranks().index(card.rank)


def lowest_card(cards):
    return min(cards, key=lambda card: (card_rank_index(card), Suits.suits().index(card.suit)))


def highest_card(cards):
    return max(cards, key=lambda card: (card_rank_index(card), Suits.suits().index(card.suit)))


def ordered_legal_bids(legal_bids):
    return sorted(legal_bids, key=lambda bid: Bids.bids().index(bid))


def ordered_cards(cards):
    return sorted(cards, key=lambda card: card.to_int())


def card_tiebreak(card):
    return (card_rank_index(card), card.to_int())


def card_beats(card, incumbent, led_suit, trump_strain):
    trump_suit = trump_strain.determine_suit() if isinstance(trump_strain, Strains) else None

    if trump_suit is not None:
        if card.suit == trump_suit and incumbent.suit != trump_suit:
            return True
        if card.suit != trump_suit and incumbent.suit == trump_suit:
            return False

    if card.suit == incumbent.suit:
        return card_rank_index(card) > card_rank_index(incumbent)
    if card.suit == led_suit and incumbent.suit != led_suit:
        return True
    return False


def current_winner(trick, trump_strain):
    if len(trick) == 0:
        return None

    led_suit = trick[0][1].suit
    winner = trick[0]
    for player, card in trick[1:]:
        if card_beats(card, winner[1], led_suit, trump_strain):
            winner = (player, card)
    return winner


def winning_legal_cards(legal_cards, trick, trump_strain):
    if len(trick) == 0:
        return list(legal_cards)

    led_suit = trick[0][1].suit
    winner = current_winner(trick, trump_strain)
    return [
        card for card in legal_cards
        if card_beats(card, winner[1], led_suit, trump_strain)
    ]


def seen_cards(all_cards, dummy_hand, card_history):
    cards = set(all_cards) | set(dummy_hand)
    for player_cards in card_history.values():
        cards.update(player_cards)
    return cards


class RuleBasedBotUser(User):
    @staticmethod
    def bid(current_player, legal_bids, bid_history):
        return pass_bid(legal_bids)

    @staticmethod
    def bid_with_hand(current_player, hand, legal_bids, bid_history):
        if len(legal_bids) == 0:
            raise ValueError("legal_bids must not be empty")

        points = high_card_points(hand)
        if Bids.REDOUBLE in legal_bids and points >= 18:
            return Bids.REDOUBLE
        if Bids.DOUBLE in legal_bids and points >= 16:
            return Bids.DOUBLE

        current_contract = getattr(bid_history, "current_contract", None)
        if getattr(current_contract, "contract", None) is not None:
            return pass_bid(legal_bids)

        if points >= 15 and is_balanced(hand):
            one_nt = contract_bid(1, Strains.NT)
            if one_nt in legal_bids:
                return one_nt

        if points >= 12:
            opening = contract_bid(1, opening_strain(hand))
            if opening in legal_bids:
                return opening

        return pass_bid(legal_bids)

    @staticmethod
    def play_card(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        if len(legal_cards) == 0:
            raise ValueError("legal_cards must not be empty")

        trump_strain = infer_contract_strain(bid_history)
        trick = current_trick(current_player, card_history, leader_history)
        if len(trick) == 0:
            lengths = suit_lengths(all_cards)
            longest_suit = max(Suits.suits(), key=lambda suit: (lengths[suit], Suits.suits().index(suit)))
            candidates = [card for card in legal_cards if card.suit == longest_suit]
            return highest_card(candidates or legal_cards)

        winner = current_winner(trick, trump_strain)
        if winner and winner[0] == current_player.partner():
            return lowest_card(legal_cards)

        winners = winning_legal_cards(legal_cards, trick, trump_strain)
        if winners:
            return lowest_card(winners)

        return lowest_card(legal_cards)


class RandomBotUser(User):
    def __init__(self, seed=0):
        self.rng = random.Random(seed)

    def bid(self, current_player, legal_bids, bid_history):
        return self._random_bid(legal_bids)

    def bid_with_hand(self, current_player, hand, legal_bids, bid_history):
        return self._random_bid(legal_bids)

    def play_card(self, current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        if len(legal_cards) == 0:
            raise ValueError("legal_cards must not be empty")
        return self.rng.choice(ordered_cards(legal_cards))

    def _random_bid(self, legal_bids):
        if len(legal_bids) == 0:
            raise ValueError("legal_bids must not be empty")
        return self.rng.choice(ordered_legal_bids(legal_bids))


class LinearPolicyBotUser(User):
    def __init__(self, bid_weights=None, card_weights=None):
        self.bid_weights = bid_weights or {
            "points": 1.0,
            "length": 1.35,
            "major": 0.8,
            "balanced_nt": 1.2,
            "level_cost": -2.6,
            "pass_floor": 10.5,
            "double_points": 0.7,
        }
        self.card_weights = card_weights or {
            "rank": 0.25,
            "wins_now": 4.0,
            "partner_winning": -3.0,
            "trump": 1.0,
            "conserve_honor": -0.4,
        }

    def bid(self, current_player, legal_bids, bid_history):
        return pass_bid(legal_bids)

    def bid_with_hand(self, current_player, hand, legal_bids, bid_history):
        if len(legal_bids) == 0:
            raise ValueError("legal_bids must not be empty")

        scored = [(self._score_bid(bid, hand, bid_history), bid) for bid in legal_bids]
        return max(scored, key=lambda item: (item[0], Bids.bids().index(item[1])))[1]

    def play_card(self, current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        if len(legal_cards) == 0:
            raise ValueError("legal_cards must not be empty")

        trump_strain = infer_contract_strain(bid_history)
        trick = current_trick(current_player, card_history, leader_history)
        scored = [
            (self._score_card(card, current_player, trick, trump_strain), card)
            for card in ordered_cards(legal_cards)
        ]
        return max(scored, key=lambda item: (item[0], *card_tiebreak(item[1])))[1]

    def _score_bid(self, bid, hand, bid_history):
        points = high_card_points(hand)
        if bid == Bids.PASS:
            return self.bid_weights["pass_floor"] - points
        if bid == Bids.DOUBLE:
            return points * self.bid_weights["double_points"] - 9
        if bid == Bids.REDOUBLE:
            return points * self.bid_weights["double_points"] - 11
        if not isinstance(bid.value, Contracts):
            return -100

        strain = bid.value.determine_strain()
        level = bid.value.determine_level()
        length = 0 if strain == Strains.NT else suit_lengths(hand)[strain.determine_suit()]
        major = strain in (Strains.HEARTS, Strains.SPADES)
        balanced_nt = strain == Strains.NT and is_balanced(hand)
        return (
            points * self.bid_weights["points"]
            + length * self.bid_weights["length"]
            + (self.bid_weights["major"] if major else 0)
            + (self.bid_weights["balanced_nt"] if balanced_nt else 0)
            + level * self.bid_weights["level_cost"]
        )

    def _score_card(self, card, current_player, trick, trump_strain):
        score = card_rank_index(card) * self.card_weights["rank"]
        trump_suit = trump_strain.determine_suit() if isinstance(trump_strain, Strains) else None
        if trump_suit is not None and card.suit == trump_suit:
            score += self.card_weights["trump"]
        if card.rank in HONOR_POINTS:
            score += HONOR_POINTS[card.rank] * self.card_weights["conserve_honor"]
        if len(trick) > 0 and card in winning_legal_cards([card], trick, trump_strain):
            score += self.card_weights["wins_now"]
        winner = current_winner(trick, trump_strain)
        if winner and winner[0] == current_player.partner():
            score += self.card_weights["partner_winning"]
        return score


class RolloutBotUser(User):
    def __init__(self, trials=64, seed=0):
        self.trials = trials
        self.seed = seed

    def bid(self, current_player, legal_bids, bid_history):
        return pass_bid(legal_bids)

    def bid_with_hand(self, current_player, hand, legal_bids, bid_history):
        return RuleBasedBotUser.bid_with_hand(current_player, hand, legal_bids, bid_history)

    def play_card(self, current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        if len(legal_cards) == 0:
            raise ValueError("legal_cards must not be empty")

        trump_strain = infer_contract_strain(bid_history)
        trick = current_trick(current_player, card_history, leader_history)
        if len(trick) == 3:
            winners = winning_legal_cards(legal_cards, trick, trump_strain)
            return lowest_card(winners) if winners else lowest_card(legal_cards)

        base_seed = self.seed + len(sum(card_history.values(), []))
        hidden_cards = [
            card for suit in Suits.suits() for rank in Ranks.ranks()
            for card in [Card(suit, rank)]
            if card not in seen_cards(all_cards, dummy_hand, card_history)
        ]

        scored = [
            (
                self._rollout_score(
                    card,
                    current_player,
                    trick,
                    trump_strain,
                    hidden_cards,
                    random.Random(base_seed + card.to_int() * 1009),
                ),
                card,
            )
            for card in ordered_cards(legal_cards)
        ]
        return max(scored, key=lambda item: (item[0], -card_rank_index(item[1]), -item[1].to_int()))[1]

    def _rollout_score(self, candidate, current_player, trick, trump_strain, hidden_cards, rng):
        wins = 0
        for _ in range(self.trials):
            simulated_trick = list(trick) + [(current_player, candidate)]
            used = {candidate}
            player = current_player
            while len(simulated_trick) < 4:
                player = player.next_player()
                legal_hidden = self._sample_legal_hidden_card(hidden_cards, used, simulated_trick, rng)
                if legal_hidden is None:
                    break
                used.add(legal_hidden)
                simulated_trick.append((player, legal_hidden))
            if len(simulated_trick) < 4:
                continue
            winner = current_winner(simulated_trick, trump_strain)
            if winner and winner[0] == current_player:
                wins += 1
        return wins / self.trials

    @staticmethod
    def _sample_legal_hidden_card(hidden_cards, used, trick, rng):
        available = [card for card in hidden_cards if card not in used]
        if len(available) == 0:
            return None
        if len(trick) == 0:
            return rng.choice(available)
        led_suit = trick[0][1].suit
        follow_suit = [card for card in available if card.suit == led_suit]
        return rng.choice(follow_suit or available)


class EnsembleBotUser(User):
    def __init__(self, bots=None):
        self.bots = bots or [
            RuleBasedBotUser(),
            LinearPolicyBotUser(),
            RolloutBotUser(trials=24, seed=17),
        ]

    def bid(self, current_player, legal_bids, bid_history):
        return pass_bid(legal_bids)

    def bid_with_hand(self, current_player, hand, legal_bids, bid_history):
        votes = [
            choose_bid_for_user(bot, current_player, hand, legal_bids, bid_history)
            for bot in self.bots
        ]
        counts = Counter(votes)
        return max(votes, key=lambda bid: (counts[bid], -Bids.bids().index(bid)))

    def play_card(self, current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        votes = [
            bot.play_card(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history)
            for bot in self.bots
        ]
        counts = Counter(votes)
        return max(votes, key=lambda card: (counts[card], -card_rank_index(card), -card.to_int()))
