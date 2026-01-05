import pygame
import csv
import random

from game.config import (
    TILE_SIZE, SCREEN_SCALE, SCREEN_W, SCREEN_H,
    MAP_PATH, TILESET_PATH, SIGN_TILE,
    BLOCKING_TILES, ENCOUNTER_TILES,
    CAPTURE_BALL_TILE, POTION_TILE, BASE_GRASS_TILE
)

from game.player import OverworldPlayer, load_player_sprites
from game.creatures import create_player_creature, create_random_enemy
from game.battle import Battle
from game.inventory import Inventory
from game.pause import PauseMenu
from game.party import PartyMenu
from game.dialogue import DialogueBox


class Overworld:
    def __init__(self, screen):
        self.screen = screen

        # Map
        self.world = self.load_map()
        self.tiles = self.load_tiles()

        # Player
        self.frames = load_player_sprites()
        self.player = OverworldPlayer(5 * TILE_SIZE, 10 * TILE_SIZE, self.frames)

        # Inventory + Party
        self.inventory = Inventory()
        self.inventory.potions = 5
        self.inventory.capture_balls = 10
        self.inventory.add_to_party(create_player_creature())  # sets active

        # Menus
        self.pause = PauseMenu()
        self.party_menu = PartyMenu()
        self.dialogue = DialogueBox()

        # Camera
        self.camx = 0
        self.camy = 0

        # State
        self.mode = "world"   # "world" or "battle"
        self.battle = None

        # Pickup popup (small, under HUD)
        self.popup_text = ""
        self.popup_timer = 0.0

        # Interact hint
        self.show_interact = False

        # Encounter control
        self.last_tile = None
        self.encounter_cd = 0.0

    # -----------------------------------------------------
    # Loading
    # -----------------------------------------------------
    def load_map(self):
        with open(MAP_PATH) as f:
            return [[int(x) for x in row] for row in csv.reader(f)]

    def load_tiles(self):
        sheet = pygame.image.load(TILESET_PATH).convert_alpha()
        tiles = []
        cols = sheet.get_width() // TILE_SIZE
        rows = sheet.get_height() // TILE_SIZE
        for y in range(rows):
            for x in range(cols):
                r = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                tile = sheet.subsurface(r).copy()
                tile = pygame.transform.scale(tile, (TILE_SIZE * SCREEN_SCALE, TILE_SIZE * SCREEN_SCALE))
                tiles.append(tile)

        return tiles

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------
    def show_popup(self, text, duration=2.0):
        self.popup_text = text
        self.popup_timer = float(duration)

    def get_tile_at(self, tx, ty):
        if ty < 0 or tx < 0 or ty >= len(self.world) or tx >= len(self.world[0]):
            return None
        return self.world[ty][tx]

    def get_player_tile(self):
        tx = self.player.rect.centerx // TILE_SIZE
        ty = self.player.rect.centery // TILE_SIZE
        return tx, ty

    def get_front_tile(self):
        dx, dy = 0, 0
        if self.player.dir == "up":
            dy = -1
        elif self.player.dir == "down":
            dy = 1
        elif self.player.dir == "left":
            dx = -1
        elif self.player.dir == "right":
            dx = 1

        ptx, pty = self.get_player_tile()
        return ptx + dx, pty + dy

    def movement_locked(self):
        return self.pause.open or self.party_menu.open or self.dialogue.open

    # -----------------------------------------------------
    # Events
    # -----------------------------------------------------
    def handle_events(self, events):
        # Dialogue eats all input first
        if self.dialogue.open:
            self.dialogue.handle(events)
            return

        # Pause toggle (world only)
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                if self.mode == "world":
                    self.pause.toggle()
                return

        # Pause menu input
        if self.pause.open:
            action = self.pause.handle(events)
            if action == "party":
                self.pause.open = False
                self.party_menu.open = True
                self.party_menu.from_battle = False
            return

        # Party menu input
        if self.party_menu.open:
            self.party_menu.handle(events, self.inventory)
            return

        # Interact (E) only in world mode
        if self.mode == "world":
            for e in events:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_e:
                    fx, fy = self.get_front_tile()
                    tid = self.get_tile_at(fx, fy)
                    if tid == SIGN_TILE:
                        self.dialogue.show("The sign reads: Welcome to Route 1!")
                    return

        # Battle input
        if self.mode == "battle" and self.battle:
            self.battle.handle_events(events)

            # battle asked to open party overlay
            if getattr(self.battle, "request_party", False):
                self.battle.request_party = False
                self.party_menu.open = True
                self.party_menu.from_battle = True
            return

    # -----------------------------------------------------
    # Update
    # -----------------------------------------------------
    def update(self, dt):
        # timers always tick
        if self.popup_timer > 0:
            self.popup_timer = max(0.0, self.popup_timer - dt)
        if self.encounter_cd > 0:
            self.encounter_cd = max(0.0, self.encounter_cd - dt)

        # Party menu still needs cooldown ticking
        if self.party_menu.open:
            self.party_menu.update(dt)

        # Battle update
        if self.mode == "battle" and self.battle:
            self.battle.update(dt)
            # keep battle synced to active
            self.battle.player = self.inventory.active

            if self.battle.state == "end":
                self.mode = "world"
                self.battle = None
                self.encounter_cd = 0.8
            return

        # World update (movement can be locked)
        old = self.player.rect.copy()
        if not self.movement_locked():
            self.player.update(dt)

        # Resolve current player tile + collisions/items/encounters
        tx, ty = self.get_player_tile()
        tid = self.get_tile_at(tx, ty)

        # Out of bounds = revert
        if tid is None:
            self.player.rect = old
            return

        # Blocking collision
        if tid in BLOCKING_TILES:
            self.player.rect = old
            return

        # Item pickups (only when movement not locked)
        if not self.movement_locked():
            if tid == POTION_TILE:
                self.inventory.potions += 1
                self.world[ty][tx] = BASE_GRASS_TILE
                self.show_popup(f"Picked up Potion x{self.inventory.potions}")

            elif tid == CAPTURE_BALL_TILE:
                self.inventory.capture_balls += 1
                self.world[ty][tx] = BASE_GRASS_TILE
                self.show_popup(f"Picked up Capture Ball x{self.inventory.capture_balls}")

        # Interact hint (based on FRONT tile, not current tile)
        self.show_interact = False
        fx, fy = self.get_front_tile()
        ftid = self.get_tile_at(fx, fy)
        if ftid == SIGN_TILE and self.mode == "world" and not self.pause.open:
            self.show_interact = True

        # Encounters (only if movement not locked)
        if (not self.movement_locked()
                and tid in ENCOUNTER_TILES
                and self.encounter_cd <= 0
                and (tx, ty) != self.last_tile):
            self.last_tile = (tx, ty)
            if random.random() < 0.12:
                enemy = create_random_enemy()
                self.battle = Battle(self.screen, self.inventory, enemy)
                self.mode = "battle"
                return

        # Camera
        map_w = len(self.world[0]) * TILE_SIZE * SCREEN_SCALE
        map_h = len(self.world) * TILE_SIZE * SCREEN_SCALE

        self.camx = int(self.player.rect.centerx * SCREEN_SCALE) - SCREEN_W // 2
        self.camy = int(self.player.rect.centery * SCREEN_SCALE) - SCREEN_H // 2

        # Clamp camera to map bounds
        self.camx = max(0, min(self.camx, map_w - SCREEN_W))
        self.camy = max(0, min(self.camy, map_h - SCREEN_H))

    # -----------------------------------------------------
    # Draw helpers
    # -----------------------------------------------------
    def draw_hud(self):
        font = pygame.font.SysFont(None, 22)

        box_w = 220
        box_h = 90
        x = SCREEN_W - box_w - 12
        y = 12

        panel = pygame.Surface((box_w, box_h))
        panel.set_alpha(180)
        panel.fill((0, 0, 0))
        self.screen.blit(panel, (x, y))

        lines = [
            "P : Pause",
            "E : Interact",
            f"Potions : {self.inventory.potions}",
            f"Capture Balls : {self.inventory.capture_balls}"
        ]
        for i, line in enumerate(lines):
            self.screen.blit(font.render(line, True, (255, 255, 255)), (x + 12, y + 10 + i * 20))

    def draw_pickup_popup(self):
        if self.popup_timer <= 0:
            return

        font = pygame.font.SysFont(None, 22)
        box_w, box_h = 220, 32
        x = SCREEN_W - box_w - 12
        y = 12 + 90 + 8  # under HUD

        panel = pygame.Surface((box_w, box_h))
        panel.set_alpha(180)
        panel.fill((0, 0, 0))
        self.screen.blit(panel, (x, y))
        self.screen.blit(font.render(self.popup_text, True, (255, 255, 255)), (x + 10, y + 8))

    def draw_interact_hint(self):
        if not self.show_interact:
            return
        font = pygame.font.SysFont(None, 20)
        txt = font.render("E : Interact", True, (255, 255, 255))

        bx = self.player.rect.x * SCREEN_SCALE - self.camx + 8
        by = self.player.rect.y * SCREEN_SCALE - self.camy - 20

        panel = pygame.Surface((txt.get_width() + 12, txt.get_height() + 6))
        panel.set_alpha(180)
        panel.fill((0, 0, 0))
        self.screen.blit(panel, (bx, by))
        self.screen.blit(txt, (bx + 6, by + 3))

    # -----------------------------------------------------
    # Draw
    # -----------------------------------------------------
    def draw(self):
        # Battle draw
        if self.mode == "battle" and self.battle:
            self.battle.draw()
            if self.party_menu.open:
                self.party_menu.draw(self.screen, SCREEN_W, SCREEN_H, self.inventory)
            return

        # World draw: map
        tile_px = TILE_SIZE * SCREEN_SCALE

        start_x = max(0, self.camx // tile_px)
        start_y = max(0, self.camy // tile_px)

        end_x = min(len(self.world[0]), (self.camx + SCREEN_W) // tile_px + 2)
        end_y = min(len(self.world), (self.camy + SCREEN_H) // tile_px + 2)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tid = self.world[y][x]
                self.screen.blit(
                    self.tiles[tid],
                    (x * tile_px - self.camx,
                     y * tile_px - self.camy)
                )

        # Player
        self.player.draw(self.screen, self.camx, self.camy)

        # UI (HUD + pickup popup + interact hint)
        self.draw_hud()
        self.draw_pickup_popup()
        self.draw_interact_hint()

        # Menus and dialogue always on top
        if self.pause.open:
            self.pause.draw(self.screen, SCREEN_W, SCREEN_H)

        if self.party_menu.open:
            self.party_menu.draw(self.screen, SCREEN_W, SCREEN_H, self.inventory)

        self.dialogue.draw(self.screen, SCREEN_W, SCREEN_H)
