from game.enums import Strains, Doubles, Contracts, InvalidDoublesException, InvalidStrainException, ContractNotFound


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
        raise TypeError("Invalid bid_trick_score")

    if not isinstance(vulnerability, bool):
        raise TypeError("vulnerability must be a bool")

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

    if doubled == Doubles.DOUBLE:
        return 50
    elif doubled == Doubles.REDOUBLE:
        return 100
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
        raise TypeError("Invalid level")

    if not isinstance(vulnerability, bool):
        raise TypeError("vulnerability must be a bool")

    if level == 6:
        return 750 if vulnerability else 500
    if level == 7:
        return 1500 if vulnerability else 1000

    return 0


def no_trump(bid, made, doubled, vulnerable):
    """
    Points for making a no trump contract

    Parameters
    ----------
    bid: int
    made: int
    doubled: Doubles
    vulnerability: bool

    Returns
    -------
    score: int

    """
    if not isinstance(bid, int):
        raise TypeError("bid must be an int")

    if not isinstance(made, int):
        raise TypeError("made must be an int")

    if not isinstance(doubled, Doubles):
        raise InvalidDoublesException()

    if not isinstance(vulnerable, bool):
        raise TypeError("vulnerability must be a bool")

    if made < bid or made not in range(1, 8):
        raise ValueError("made must be between 1 and 8 and be less than bid")

    multiplier = 1
    overtrick = 30

    if doubled == Doubles.DOUBLE:
        multiplier = 2
        overtrick = 100 if not vulnerable else 200
    elif doubled == Doubles.REDOUBLE:
        multiplier = 4
        overtrick = 200 if not vulnerable else 400

    bid_trick_score = (30 * bid + 10) * multiplier
    overtrick_score = overtrick * (made - bid)
    bonus = contract_bonus(bid_trick_score, vulnerable) + doubled_bonus(doubled) + slam_bonus(bid, vulnerable)

    return bid_trick_score + overtrick_score + bonus


def major(bid, made, doubled, vulnerable):
    """
    Points for making a major contract

    Parameters
    ----------
    bid: int
    made: int
    doubled: Doubles
    vulnerability: bool

    Returns
    -------
    score: int

    """
    if not isinstance(bid, int):
        raise TypeError("bid must be an int")

    if not isinstance(made, int):
        raise TypeError("made must be an int")

    if not isinstance(doubled, Doubles):
        raise InvalidDoublesException()

    if not isinstance(vulnerable, bool):
        raise TypeError("vulnerability must be a bool")

    if made < bid or made not in range(1, 8):
        raise ValueError("made must be between 1 and 8 and be less than bid")

    multiplier = 1
    overtrick = 30

    if doubled == Doubles.DOUBLE:
        multiplier = 2
        overtrick = 100 if not vulnerable else 200
    elif doubled == Doubles.REDOUBLE:
        multiplier = 4
        overtrick = 200 if not vulnerable else 400

    bid_trick_score = 30 * bid * multiplier
    overtrick_score = overtrick * (made - bid)
    bonus = contract_bonus(bid_trick_score, vulnerable) + doubled_bonus(doubled) + slam_bonus(bid, vulnerable)

    return bid_trick_score + overtrick_score + bonus


def minor(bid, made, doubled, vulnerability):
    """
    Points for making a minor contract

    Parameters
    ----------
    bid: int
    made: int
    doubled: Doubles
    vulnerability: bool

    Returns
    -------
    score: int

    """
    if not isinstance(bid, int):
        raise TypeError("bid must be an int")

    if not isinstance(made, int):
        raise TypeError("made must be an int")

    if not isinstance(doubled, Doubles):
        raise InvalidDoublesException()

    if not isinstance(vulnerability, bool):
        raise TypeError("vulnerability must be a bool")

    if made < bid or made not in range(1, 8):
        raise ValueError("made must be between 1 and 8 and be less than bid")

    multiplier = 1
    overtrick = 20

    if doubled == Doubles.DOUBLE:
        multiplier = 2
        overtrick = 100 if not vulnerability else 200
    elif doubled == Doubles.REDOUBLE:
        multiplier = 4
        overtrick = 200 if not vulnerability else 400

    bid_trick_score = 20 * bid * multiplier
    overtrick_score = overtrick * (made - bid)
    bonus = contract_bonus(bid_trick_score, vulnerability) + doubled_bonus(doubled) + slam_bonus(bid, vulnerability)

    return bid_trick_score + overtrick_score + bonus


def penalty(down, doubled, vulnerability):
    """
    Points for setting a contract

    Parameters
    ----------
    down: int
    doubled: Doubles
    vulnerability: bool

    Returns
    -------
    penelty: int

    """
    if not isinstance(down, int):
        raise TypeError("down must be of type int")

    if down not in range(1, 14):
        raise ValueError("down must be between 1 and 14")

    if not isinstance(doubled, Doubles):
        raise InvalidDoublesException()

    if not isinstance(vulnerability, bool):
        raise TypeError("vulnerability must be a bool")

    if doubled == Doubles.NONE:
        return (down * 100) if vulnerability else (down * 50)
    elif doubled == Doubles.DOUBLE:
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


def calculate_score(bid, strain, result, doubled, vulnerability):
    """
    Calculating the score from a contract and result

    Parameters
    ----------
    bid: int
    strain: Strains
    result: int
    doubled: Doubles
    vulnerability: bool

    Returns
    -------
    score: int

    """
    if not isinstance(bid, int):
        raise TypeError("bid must be an int")

    if not isinstance(strain, Strains):
        raise InvalidStrainException()

    if not isinstance(result, int):
        raise TypeError("result must be an int")

    if not isinstance(doubled, Doubles):
        raise InvalidDoublesException()

    if not isinstance(vulnerability, bool):
        raise TypeError("vulnerability must be a bool")

    if result not in range(-13,8):
        raise ValueError("result must be between -13 and 8")

    if result == 0:
        raise ValueError("result must not be 0")

    if result < 0:
        return -1 * penalty(-1*result, doubled, vulnerability)
    elif strain in [Strains.CLUBS, Strains.DIAMONDS]:
        return minor(bid,result, doubled, vulnerability)
    elif strain in [Strains.HEARTS, Strains.SPADES]:
        return major(bid, result, doubled, vulnerability)
    else:
        return no_trump(bid, result, doubled, vulnerability)


def get_score_from_result(contract, doubled, tricks_taken, vulnerability):
    contracts = Contracts.contracts()
    strains = Strains.strains()

    if contract not in contracts:
        raise ContractNotFound("Invalid contract")

    bid = contract.determine_level()
    strain = contract.determine_strain()

    required_number_of_tricks = bid + 6

    if tricks_taken >= required_number_of_tricks:
        result = tricks_taken - 6
    else:
        result = tricks_taken - required_number_of_tricks #Should be a negative number

    return calculate_score(bid, strain, result, doubled, vulnerability)
