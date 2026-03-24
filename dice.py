from singleton import Singleton
from pyparsing import Word, nums, oneOf, Optional
from typing import Tuple, List
import random


@Singleton
class Dice(object):
    # wzorzec: [count]k/K/d/D<sides>[±*/<mod>]
    count = (
        Optional(Word(nums), default="1")
        .setParseAction(lambda t: int(t[0]))
        .setName("count")
    )
    dice_type = oneOf("k K d D").setName("dice_type")
    sides = Word(nums).setParseAction(lambda t: int(t[0])).setName("sides")
    mod_op = oneOf("- + * /").setName("mod_op")  # operator
    mod_val = Word(nums).setParseAction(lambda t: int(t[0])).setName("mod_val")

    dice_token = (
        count
        + dice_type
        + sides
        + Optional(mod_op + mod_val)
    )

    def __init__(self):
        pass

    def __str__(self):
        return 'kostka'

    def roll_dice(self, count: int, sides: int) -> Tuple[int, List[int]]:
        rolls = [random.randint(1, sides) for _ in range(count)]
        return sum(rolls), rolls

    def roll_dice_explode(self, count: int, sides: int) -> Tuple[int, List[int]]:
        rolls = []
        for _ in range(count):
            r = 0
            parts = []  
            while True:
                val = random.randint(1, sides)
                parts.append(val)
                r += val
                if val < sides:
                    break
            rolls.append(r)
        return sum(rolls), rolls

    def roll(self, dice_str: str) -> str:
        try:
            tokens = self.dice_token.parseString(dice_str.strip(), parseAll=True).asList()
        except Exception as e:
            return(f"Nie wiem co to za kości {dice_str}")
        count = tokens[0]
        dice_type = tokens[1]
        sides = tokens[2]
        mod = None
        mod_op = None
        if len(tokens) >= 4:
            mod_op = tokens[3]
            mod = tokens[4]
        if dice_type in "kK":
            func = self.roll_dice_explode if dice_type == "K" else self.roll_dice
        elif dice_type in "dD":
            func = self.roll_dice_explode if dice_type == "D" else self.roll_dice
        else:
            return (f"Nie wiem co to za kości: {dice_type}")
        total_dice, rolls = func(count, sides)
        rolls_str = "+".join(map(str, rolls))
        if count == 1:
            rolls_str = str(rolls[0])
        if mod is not None:
            if mod_op == "+":
                result = total_dice + mod
                formula = f"({rolls_str})+{mod}"
            elif mod_op == "-":
                result = total_dice - mod
                formula = f"({rolls_str})-{mod}"
            elif mod_op == "*":
                result = total_dice * mod
                formula = f"({rolls_str})*{mod}"
            elif mod_op == "/":
                if mod != 0:
                    result = total_dice // mod 
                else:
                    return ("Dzielenie przez 0")
                formula = f"({rolls_str})/{mod}"
            else:
                return (f"Nieznany operator: {mod_op}")
        else:
            result = total_dice
            formula = rolls_str

        return f"{result} ({formula})"