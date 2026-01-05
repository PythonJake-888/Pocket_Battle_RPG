import pygame, os, random
from game.config import BATTLE_DIR

class Creature:
    def __init__(self, name, hp, atk, dfn, spd, sprite):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.dfn = dfn
        self.spd = spd
        self.sprite = sprite
        self.moves = []


def load_sprite(fname):
    path = os.path.join(BATTLE_DIR, fname)
    try:
        return pygame.image.load(path).convert_alpha()
    except:
        s = pygame.Surface((96,96), pygame.SRCALPHA)
        s.fill((200,50,50))
        return s


def create_player_creature():
    m = Creature("Raccoon", 100, 18, 10, 12, load_sprite("raccoon_front.png"))
    m.moves = [
        {"name": "Quick Swipe", "power": 16},
        {"name": "Heavy Pounce", "power": 25}
    ]
    return m


def create_random_enemy():
    python = Creature("Python", 120, 20, 14, 8, load_sprite("python_front.png"))
    python.moves = [
        {"name": "Constrict", "power": 20},
        {"name": "Venom Bite", "power": 24}
    ]

    raven = Creature("Raven", 90, 16, 12, 25, load_sprite("raven_front.png"))
    raven.moves = [
        {"name": "Peck", "power": 15},
        {"name": "Wing Slash", "power": 22}
    ]

    return random.choice([python, raven])


def create_player_creature():
    m=Creature("Raccoon",100,18,10,12,load_sprite("raccoon_front.png"))
    m.moves=[{"name":"Swipe","power":18},{"name":"Pounce","power":25}]
    return m

def create_random_enemy():
    return random.choice([
        Creature("Python",120,20,14,8,load_sprite("python_front.png")),
        Creature("Raven",90,16,12,25,load_sprite("raven_front.png"))
    ])
def calculate_damage(attacker, defender, move):
    base = move["power"]
    dmg = base + attacker.atk - defender.dfn
    return max(1, dmg + random.randint(-2, 2))

