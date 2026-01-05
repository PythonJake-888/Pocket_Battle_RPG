class Inventory:
    def __init__(self):
        self.potions = 0
        self.capture_balls = 0

        # Party system
        self.party = []
        self.active = None

    # ------------------ Items ------------------

    def heal(self, creature, amount=40):
        if self.potions <= 0:
            return False
        if creature.hp <= 0:
            return False  # ❌ cannot revive
        if creature.hp >= creature.max_hp:
            return False

        creature.hp = min(creature.max_hp, creature.hp + amount)
        self.potions -= 1
        return True

    # ------------------ Party ------------------

    def add_to_party(self, creature):
        self.party.append(creature)
        if self.active is None:
            self.active = creature

    def set_active(self, creature):
        if creature in self.party and creature.hp > 0:
            self.active = creature
            return True
        return False

    def remove_from_party(self, creature):
        if creature not in self.party:
            return False

        # Cannot delete last living creature
        living = [m for m in self.party if m.hp > 0]
        if creature in living and len(living) <= 1:
            return False

        self.party.remove(creature)

        if creature is self.active:
            self.active = living[0] if living else None

        return True

    # ------------------ Battle Helpers ------------------

    def has_usable(self):
        return any(m.hp > 0 for m in self.party)
