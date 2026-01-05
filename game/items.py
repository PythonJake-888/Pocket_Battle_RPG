class Inventory:
    def __init__(self):
        self.potions = 5
        self.balls = 3

    def heal(self, creature):
        if self.potions <= 0:
            return False, "No potions left!"
        if creature.hp >= creature.max_hp:
            return False, f"{creature.name} is already full HP."

        heal = min(30, creature.max_hp - creature.hp)
        creature.hp += heal
        self.potions -= 1
        return True, f"{creature.name} healed {heal} HP!"
