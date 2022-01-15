import random
import sys

ROLLS_N = 6 * 6 / 2

def all_rolls():
    for i in range(1, 7):
        for j in range(i, 7):
            yield (i, j)

def disregard_order(roll):
    return (min(roll), max(roll))

def dice_roll():
    first = random.randrange(6)+1
    second = random.randrange(6)+1
    return (first, second)

def first_roll():
    roll = dice_roll()
    while roll[0] == roll[1]:
        roll = dice_roll()
    return roll

def init():
    if len(sys.argv) > 1:
        random.seed(int(sys.argv[1]))
