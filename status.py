COND_POISON = 1

BITS = "StatusBits"
PWR = "PoisonPower"
TRN = "PoisonTurns"
TCK = "PoisonTick"

def init(hero):
    if BITS not in hero:
        hero[BITS] = 0
    if PWR not in hero:
        hero[PWR] = 0
    if TRN not in hero:
        hero[TRN] = 0
    if TCK not in hero:
        hero[TCK] = 0
    if hero.get(TRN, 0) > 0:
        hero[BITS] |= COND_POISON
    else:
        hero[BITS] &= ~COND_POISON

def has(hero, cond):
    return (hero.get(BITS, 0) & cond) != 0

def weak_poison(hero):
    hero[BITS] = hero.get(BITS, 0) | COND_POISON
    hero[PWR] = 1
    hero[TRN] = 8
    hero[TCK] = 0

def clear_poison(hero):
    hero[BITS] = hero.get(BITS, 0) & ~COND_POISON
    hero[PWR] = 0
    hero[TRN] = 0
    hero[TCK] = 0

def clear_all(hero):
    hero[BITS] = 0
    hero[PWR] = 0
    hero[TRN] = 0
    hero[TCK] = 0

def tick(hero):
    if not has(hero, COND_POISON):
        return 0
    turns = int(hero.get(TRN, 0))
    if turns <= 0:
        clear_poison(hero)
        return 0
    t = int(hero.get(TCK, 0)) + 1
    turns -= 1
    dmg = 0
    if t >= 2:
        dmg = int(hero.get(PWR, 1))
        if dmg < 1:
            dmg = 1
        t = 0
    hero[TRN] = turns
    hero[TCK] = t
    if turns <= 0:
        clear_poison(hero)
    if dmg:
        hero["HP"] -= dmg
        if hero["HP"] < 0:
            hero["HP"] = 0
    return dmg
