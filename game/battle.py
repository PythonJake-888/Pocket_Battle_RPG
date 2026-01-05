import pygame, random
from game.creatures import calculate_damage


class Battle:
    def __init__(self, screen, inventory, enemy):
        self.screen = screen
        self.inventory = inventory

        self.player = inventory.active
        self.enemy = enemy

        self.state = "menu"   # menu, fight, bag, message, end
        self.menu_cursor = 0
        self.move_cursor = 0
        self.bag_cursor = 0
        self.key_cd = 0.0

        self.message = ""
        self.request_party = False

        self.message_close = False

        self.force_end = False

    # -----------------------------------------------------

    def handle_events(self, events):
        if self.key_cd > 0:
            return

        self.player = self.inventory.active

        for e in events:
            if e.type != pygame.KEYDOWN:
                continue

            k = e.key

            # UNIVERSAL BACK
            if k in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                if self.state in ("fight", "bag"):
                    self.state = "menu"
                    self.key_cd = 0.15
                    return
                if self.state == "message":
                    if k in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.message_close:
                            self.state = "end"
                            self.message_close = False
                        elif self.enemy.hp <= 0 or self.player.hp <= 0:
                            self.state = "end"
                        else:
                            self.state = "menu"
                        self.key_cd = 0.15

            # ---------------- MAIN MENU ----------------
            if self.state == "menu":
                if k in (pygame.K_LEFT, pygame.K_a):
                    self.menu_cursor = (self.menu_cursor - 1) % 4
                elif k in (pygame.K_RIGHT, pygame.K_d):
                    self.menu_cursor = (self.menu_cursor + 1) % 4
                elif k in (pygame.K_RETURN, pygame.K_SPACE):
                    choice = ["FIGHT", "BAG", "PARTY", "RUN"][self.menu_cursor]

                    if choice == "FIGHT":
                        self.state = "fight"
                        self.move_cursor = 0

                    elif choice == "BAG":
                        self.state = "bag"
                        self.bag_cursor = 0

                    elif choice == "PARTY":
                        self.request_party = True

                    elif choice == "RUN":
                        self.state = "end"

                    self.key_cd = 0.15
                return

            # ---------------- FIGHT ----------------
            if self.state == "fight":
                moves = self.player.moves if self.player.moves else [{"name": "Struggle", "power": 10}]
                self.player.moves = moves

                if k in (pygame.K_LEFT, pygame.K_a):
                    self.move_cursor = (self.move_cursor - 1) % len(moves)
                elif k in (pygame.K_RIGHT, pygame.K_d):
                    self.move_cursor = (self.move_cursor + 1) % len(moves)
                elif k in (pygame.K_RETURN, pygame.K_SPACE):
                    move = moves[self.move_cursor]
                    dmg = calculate_damage(self.player, self.enemy, move)
                    self.enemy.hp = max(0, self.enemy.hp - dmg)

                    if self.enemy.hp <= 0:
                        self.message = f"{self.enemy.name} fainted!"
                        self.state = "message"
                    else:
                        self.enemy_attack()

                    self.key_cd = 0.18
                return

            # ---------------- BAG ----------------
            if self.state == "bag":
                if k in (pygame.K_LEFT, pygame.K_a):
                    self.bag_cursor = (self.bag_cursor - 1) % 2
                elif k in (pygame.K_RIGHT, pygame.K_d):
                    self.bag_cursor = (self.bag_cursor + 1) % 2
                elif k in (pygame.K_RETURN, pygame.K_SPACE):

                    # Potion
                    if self.bag_cursor == 0:
                        if self.inventory.potions > 0:
                            self.request_party = True
                            self.state = "menu"  # ← freeze battle while party menu is open
                            return
                        else:
                            self.message = "No potions!"
                            self.state = "message"



                    # Capture Ball
                    elif self.bag_cursor == 1:
                        if self.inventory.capture_balls <= 0:
                            self.message = "No capture balls!"
                            self.state = "message"
                        else:
                            self.inventory.capture_balls -= 1
                            chance = max(0.05, min(0.85, 1 - self.enemy.hp / self.enemy.max_hp))
                            if random.random() < chance:
                                self.message = f"You caught {self.enemy.name}!"
                                self.inventory.add_to_party(self.enemy)
                                self.state = "message"
                                self.message_close = True  # ← mark that this message should auto-exit
                                self.key_cd = 0.2
                                return


                            else:
                                self.message = "It broke free!"
                                self.enemy_attack()

                    self.key_cd = 0.18
                return

            # ---------------- MESSAGE ----------------
            if self.state == "message":
                if k in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.message_close:
                        self.state = "end"
                        self.message_close = False
                    elif self.enemy.hp <= 0 or self.player.hp <= 0:
                        self.state = "end"
                    else:
                        self.state = "menu"
                    self.key_cd = 0.2

    # -----------------------------------------------------

    def enemy_attack(self):
        # Refresh active creature
        self.player = self.inventory.active

        # Emergency move fallback
        if not self.enemy.moves:
            self.enemy.moves = [{"name": "Struggle", "power": 10}]

        move = random.choice(self.enemy.moves)
        dmg = calculate_damage(self.enemy, self.player, move)
        self.player.hp = max(0, self.player.hp - dmg)

        # If active fainted, force party switch
        if self.player.hp <= 0:

            # Are there any living creatures left?
            if self.inventory.has_usable():
                self.message = f"{self.player.name} fainted! Choose another creature."
                self.request_party = True
                self.state = "menu"  # freeze battle until switch
            else:
                # All fainted → real loss
                self.message = f"{self.player.name} fainted!"
                self.state = "message"
        else:
            self.state = "menu"

    # -----------------------------------------------------

    def update(self, dt):
        self.key_cd = max(0.0, self.key_cd - dt)
        self.player = self.inventory.active

    # -----------------------------------------------------

    def draw_hp_bar(self, name, hp, maxhp, x, y):
        maxhp = max(1, maxhp)
        hp = max(0, min(hp, maxhp))
        pygame.draw.rect(self.screen,(0,0,0),(x,y,220,22))
        pygame.draw.rect(self.screen,(0,200,0),(x+2,y+2,int((hp/maxhp)*216),18))
        font = pygame.font.SysFont(None,22)
        self.screen.blit(font.render(f"{name} {hp}/{maxhp}",True,(0,0,0)),(x,y-20))

    # -----------------------------------------------------

    def draw(self):
        # Use the REAL window size (fixes the empty space issue)
        W, H = self.screen.get_size()

        # Layout constants
        PANEL_H = 150
        PANEL_Y = H - PANEL_H
        BORDER = 4

        # Background (fill ALL of the screen)
        self.screen.fill((140, 160, 220))  # sky

        # --- Ground planes (positioned relative to screen size) ---
        # Player ground (lower-left area)
        pygame.draw.ellipse(
            self.screen, (60, 130, 60),
            (int(W * 0.08), int(H * 0.58), int(W * 0.42), int(H * 0.12))
        )

        # Enemy ground (upper-right area)
        pygame.draw.ellipse(
            self.screen, (60, 130, 60),
            (int(W * 0.55), int(H * 0.26), int(W * 0.36), int(H * 0.10))
        )

        # --- Enemy ---
        self.draw_hp_bar(self.enemy.name, self.enemy.hp, self.enemy.max_hp, int(W * 0.52), int(H * 0.06))
        enemy_sprite = pygame.transform.scale(self.enemy.sprite, (160, 160))
        self.screen.blit(enemy_sprite, (int(W * 0.62), int(H * 0.18)))

        # --- Player ---
        self.draw_hp_bar(self.player.name, self.player.hp, self.player.max_hp, int(W * 0.10), int(H * 0.36))
        player_sprite = pygame.transform.scale(self.player.sprite, (180, 180))
        self.screen.blit(player_sprite, (int(W * 0.12), int(H * 0.44)))

        # --- Bottom UI Panel (ALWAYS at the bottom, no matter window size) ---
        pygame.draw.rect(self.screen, (20, 20, 60), (0, PANEL_Y, W, PANEL_H))
        pygame.draw.rect(self.screen, (255, 255, 255), (0, PANEL_Y, W, PANEL_H), BORDER)

        font = pygame.font.SysFont(None, 36)
        hint = pygame.font.SysFont(None, 22)

        self.screen.blit(
            hint.render("WASD/Arrows • Enter select • Backspace/Esc back", True, (210, 210, 210)),
            (16, PANEL_Y + 6)
        )

        # --- Menus ---
        if self.state == "menu":
            opts = ["FIGHT", "BAG", "PARTY", "RUN"]
            for i, opt in enumerate(opts):
                col = (255, 255, 0) if i == self.menu_cursor else (230, 230, 230)
                x = int(W * 0.10) + int(W * 0.22) * i
                self.screen.blit(font.render(opt, True, col), (x, PANEL_Y + 60))

        elif self.state == "fight":
            moves = self.player.moves if getattr(self.player, "moves", None) else [{"name": "Struggle", "power": 10}]
            for i, m in enumerate(moves[:4]):  # keep it clean if more than 4
                col = (255, 255, 0) if i == self.move_cursor else (230, 230, 230)
                x = int(W * 0.08) + int(W * 0.24) * i
                self.screen.blit(font.render(m["name"], True, col), (x, PANEL_Y + 60))

        elif self.state == "bag":
            items = [f"Potion x{self.inventory.potions}", f"Capture Ball x{self.inventory.capture_balls}"]
            for i, it in enumerate(items):
                col = (255, 255, 0) if i == self.bag_cursor else (230, 230, 230)
                x = int(W * 0.18) + int(W * 0.35) * i
                self.screen.blit(font.render(it, True, col), (x, PANEL_Y + 60))

        elif self.state == "message":
            big = pygame.font.SysFont(None, 42)
            self.screen.blit(big.render(self.message, True, (255, 255, 255)), (int(W * 0.08), PANEL_Y + 60))


