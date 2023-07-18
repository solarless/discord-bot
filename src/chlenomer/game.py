import math
import random
from chlenomer.database import Player


LEVELS_TO_RATES = {
    1: 100,
    2: 300,
    3: 750,
    4: 1500,
    5: 2250,
}

LEVEL_PRICES = {
    2: 800,
    3: 3000,
    4: 9000,
    5: 24000,
}

MAX_BETS_PER_COOLDOWN = 15


def reset_cooldowns():
    Player.update(mined=False, bets=0).execute()


def calculate_mining_amount(rate: int):
    deviation = math.floor(rate * 0.25)
    min = rate - deviation
    max = rate + deviation
    return random.randint(min, max)


def mine_coins(player: Player):
    rate = LEVELS_TO_RATES[player.level]
    amount = calculate_mining_amount(rate)
    player.coins += amount
    player.mined = True
    player.save()
    return amount
