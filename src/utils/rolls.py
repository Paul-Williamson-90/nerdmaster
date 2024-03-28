import random

def normal_roll(dc: int, modifier: int = 0)->bool:
    max_roll = 0
    modifier = max([0, modifier])
    for _ in range(modifier):
        max_roll = max([max_roll, random.randint(1, 100)])
    return max_roll >= dc