from BridgeBot.bidding import strains

dbl = ["","X","XX"]

def contract_bonus(bid_trick_score, vuln):
    if bid_trick_score < 100:
        return 50

    if vuln:
        return 500

    return 300


def doubled_bonus(doubled):
    if doubled in ["X","XX"]:
        return 50
    else:
        return 0


def slam_bonus(level,vuln):
    if level == 6:
        return 750 if vuln else 500
    if level == 7:
        return 1500 if vuln else 1000

    return 0


def no_trump(bid,made,doubled,vuln):
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
    bonus = contract_bonus(bid_trick_score,vuln) + doubled_bonus(doubled) + slam_bonus(bid,vuln)

    return bid_trick_score + overtrick_score + bonus


def major(bid,made,doubled,vuln):
    if doubled not in dbl:
        return "INVALID"

    if made < bid or made not in range(1, 8):
        return "INVALID"

    multiplier = 1

    if doubled == "X":
        multiplier = 2
    elif doubled == "XX":
        multiplier = 4

    bid_trick_score = 30 * bid * multiplier
    overtrick_score = (30 * (made - bid)) * multiplier
    bonus = contract_bonus(bid_trick_score, vuln) + doubled_bonus(doubled) + slam_bonus(bid,vuln)

    return bid_trick_score + overtrick_score + bonus


def minor(bid,made,doubled,vuln):
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
    bonus = contract_bonus(bid_trick_score, vuln) + doubled_bonus(doubled) + slam_bonus(bid,vuln)

    return bid_trick_score + overtrick_score + bonus


def penalty(down,doubled,vuln):
    if doubled not in dbl:
        return "INVALID"

    if down not in range(1, 14):
        return "INVALID"

    if doubled == "":
        return (down * 100) if vuln else (down * 50)
    elif doubled == "X":
        if down == 1:
            return 200 if vuln else 100
        elif down == 2:
            return 500 if vuln else 300
        elif down == 3:
            return 800 if vuln else 500
        else:
            base = 800 if vuln else 500
            return base + (down - 3)*300
    else: # redoubled
        if down == 1:
            return 400 if vuln else 200
        elif down == 2:
            return 1000 if vuln else 600
        elif down == 3:
            return 1600 if vuln else 1000
        else:
            base = 1600 if vuln else 1000
            return base + (down - 3)*600


def score(bid,strain,result,doubled,vuln):
    if strain not in strains:
        return "INVALID"

    if doubled not in dbl:
        return "INVALID"

    if result not in range(-13,8):
        return "INVALID"

    if result == 0:
        return "INVALID"

    if result < 0:
        return penalty(-1*result,doubled,vuln)
    elif strain in ["CLUBS","DIAMONDS"]:
        return minor(bid,result,doubled,vuln)
    elif strain in ["HEARTS","SPADES"]:
        return major(bid,result,doubled,vuln)
    else:
        return no_trump(bid,result,doubled,vuln)

