from enums import Strains, Doubles, InvalidDoublesException, InvalidStrainException

def contract_bonus(bid_trick_score, vulnerability):
    """
    Determine the contract bonus
    Parameters
    ----------
    bid_trick_score: int
    vulnerability: bool

    Returns
    -------
    contract_bonus: int

    """
    if not isinstance(bid_trick_score, int):
        raise ValueError("Invalid bid_trick_score")

    if not isinstance(vulnerability, bool):
        raise ValueError("vulnerability must be a bool")

    if bid_trick_score < 100:
        return 50

    if vulnerability:
        return 500

    return 300


def doubled_bonus(doubled):
    """
    Calculate doubled bonus

    Parameters
    ----------
    doubled: Doubles

    Returns
    -------
    points: int

    """
    if not isinstance(doubled, Doubles):
        raise InvalidDoublesException("Invalid Doubles")

    if doubled in [Doubles.DOUBLE, Doubles.DOUBLE_DOWN]:
        return 50
    else:
        return 0


def slam_bonus(level, vulnerability):
    """
    Calculate slam bonus

    Parameters
    ----------
    level: int
    vulnerability: bool

    Returns
    -------
    bonus: int

    """
    if not isinstance(level, int):
        raise ValueError("Invalid level")

    if not isinstance(vulnerability, bool):
        raise ValueError("vulnerability must be a bool")

    if level == 6:
        return 750 if vulnerability else 500
    if level == 7:
        return 1500 if vulnerability else 1000

    return 0


def no_trump(bid,made,doubled, vulnerability):
    if doubled not in dbl:
        return "INVALID"

    if made < bid or made not in range(1,8):
        return "INVALID"

    multiplier = 1

    if doubled == "X":
        multiplier = 2
    elif doubled == "XX":
        multiplier = 4

    bid_trick_score = (30 * bid + 10) * multiplier
    overtrick_score = (30 * (made - bid)) * multiplier
    bonus = contract_bonus(bid_trick_score, vulnerability) + doubled_bonus(doubled) + slam_bonus(bid, vulnerability)

    return bid_trick_score + overtrick_score + bonus


def major(bid, made, doubled, vulnerability):
    if doubled not in dbl:
        return "INVALID"

    if made < bid or made not in range(1, 8):
        return "INVALID"

    multiplier = 1

    if doubled == Doubles.DOUBLE:
        multiplier = 2
    elif doubled == Doubles.DOUBLE_DOWN:
        multiplier = 4

    bid_trick_score = 30 * bid * multiplier
    overtrick_score = (30 * (made - bid)) * multiplier
    bonus = contract_bonus(bid_trick_score, vulnerability) + doubled_bonus(doubled) + slam_bonus(bid, vulnerability)

    return bid_trick_score + overtrick_score + bonus


def minor(bid,made, doubled, vulnerability):
    if doubled not in dbl:
        return "INVALID"

    if made < bid or made not in range(1, 8):
        return "INVALID"

    multiplier = 1

    if doubled == "X":
        multiplier = 2
    elif doubled == "XX":
        multiplier = 4

    bid_trick_score = 20 * bid * multiplier
    overtrick_score = (20 * (made - bid)) * multiplier
    bonus = contract_bonus(bid_trick_score, vulnerability) + doubled_bonus(doubled) + slam_bonus(bid, vulnerability)

    return bid_trick_score + overtrick_score + bonus


def penalty(down, doubled, vulnerability):
    if doubled not in dbl:
        return "INVALID"

    if down not in range(1, 14):
        return "INVALID"

    if doubled == "":
        return (down * 100) if vulnerability else (down * 50)
    elif doubled == "X":
        if down == 1:
            return 200 if vulnerability else 100
        elif down == 2:
            return 500 if vulnerability else 300
        elif down == 3:
            return 800 if vulnerability else 500
        else:
            base = 800 if vulnerability else 500
            return base + (down - 3)*300
    else: # redoubled
        if down == 1:
            return 400 if vulnerability else 200
        elif down == 2:
            return 1000 if vulnerability else 600
        elif down == 3:
            return 1600 if vulnerability else 1000
        else:
            base = 1600 if vulnerability else 1000
            return base + (down - 3)*600


def score(bid, strain, result, doubled, vulnerability):
    if not isinstance(strain, Strains):
        raise InvalidStrainException()

    if not isinstance(doubled, Doubles):
        raise InvalidDoublesException()

    if result not in range(-13,8):
        raise ValueError("result must be between -13 and 8")

    if result == 0:
        raise ValueError("result must not be 0")

    if result < 0:
        return penalty(-1*result, doubled, vulnerability)
    elif strain in [Strains.CLUBS, Strains.DIAMONDS]:
        return minor(bid,result, doubled, vulnerability)
    elif strain in [Strains.HEARTS, Strains.SPADES]:
        return major(bid, result, doubled, vulnerability)
    else:
        return no_trump(bid, result, doubled, vulnerability)

