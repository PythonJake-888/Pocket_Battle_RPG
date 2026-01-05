import os

# Screen
TILE_SIZE = 32
SCREEN_SCALE = 4
BASE_W, BASE_H = 200, 200
SCREEN_W = BASE_W * SCREEN_SCALE
SCREEN_H = BASE_H * SCREEN_SCALE
FPS = 60

# Paths
ASSETS_DIR = "assets"
MAPS_DIR = os.path.join(ASSETS_DIR, "maps")
TILES_DIR = os.path.join(ASSETS_DIR, "tiles")
OVERWORLD_DIR = os.path.join(ASSETS_DIR, "overworld")
BATTLE_DIR = os.path.join(ASSETS_DIR, "battle")


MAP_PATH = os.path.join(MAPS_DIR, "route1.csv")
TILESET_PATH = os.path.join(TILES_DIR, "tileset.png")

# Tile behavior
BLOCKING_TILES = {5,6,12,13,14,20,21,24,26,27,28,32,34,35,36,37,39,42}
ENCOUNTER_TILES = {15,22,23,38,51,52,53,58,59,60,61,62}

SIGN_TILE = 28    # use your actual sign tile ID

CAPTURE_BALL_TILE = 30
POTION_TILE = 31
BASE_GRASS_TILE = 0

BATTLE_TOP = 300
BATTLE_GROUND = 390
BATTLE_UI_Y = 450
