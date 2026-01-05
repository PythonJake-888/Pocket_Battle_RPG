import pygame

class PartyMenu:
    def __init__(self):
        self.open = False
        self.index = 0

        self.action_open = False
        self.action_index = 0
        self.actions = ["SET ACTIVE", "HEAL", "RELEASE", "BACK"]

        self.key_cd = 0.0

    # ----------------------------
    def update(self, dt):
        self.key_cd = max(0.0, self.key_cd - dt)

    # ----------------------------
    def close(self):
        self.open = False
        self.action_open = False

    # ----------------------------
    def handle(self, events, inventory):
        if self.key_cd > 0:
            return None

        party = inventory.party
        if not party:
            return None

        # clamp index
        self.index = max(0, min(self.index, len(party) - 1))

        for e in events:
            if e.type != pygame.KEYDOWN:
                continue

            k = e.key

            # universal back
            if k in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                if self.action_open:
                    self.action_open = False
                else:
                    self.close()
                self.key_cd = 0.15
                return None

            # -------- PARTY LIST --------
            if not self.action_open:
                if k in (pygame.K_UP, pygame.K_w):
                    self.index = (self.index - 1) % len(party)
                    self.key_cd = 0.12

                elif k in (pygame.K_DOWN, pygame.K_s):
                    self.index = (self.index + 1) % len(party)
                    self.key_cd = 0.12

                elif k in (pygame.K_RETURN, pygame.K_SPACE):
                    self.action_open = True
                    self.action_index = 0
                    self.key_cd = 0.15

            # -------- ACTION MENU --------
            else:
                if k in (pygame.K_UP, pygame.K_w):
                    self.action_index = (self.action_index - 1) % len(self.actions)
                    self.key_cd = 0.12

                elif k in (pygame.K_DOWN, pygame.K_s):
                    self.action_index = (self.action_index + 1) % len(self.actions)
                    self.key_cd = 0.12

                elif k in (pygame.K_RETURN, pygame.K_SPACE):
                    mon = party[self.index]
                    choice = self.actions[self.action_index]

                    if choice == "SET ACTIVE":
                        inventory.set_active(mon)
                        self.action_open = False  # stay in party menu


                    elif choice == "HEAL":
                        inventory.heal(mon)

                    elif choice == "RELEASE":
                        inventory.remove_from_party(mon)
                        self.index = min(self.index, len(inventory.party) - 1)

                    elif choice == "BACK":
                        self.action_open = False

                    self.key_cd = 0.15

        return None

    # ----------------------------
    def draw(self, screen, SW, SH, inventory):
        party = inventory.party
        if not party:
            return

        # dark overlay
        panel = pygame.Surface((SW, SH), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 200))
        screen.blit(panel, (0, 0))

        title_font = pygame.font.SysFont(None, 56, bold=True)
        ui = pygame.font.SysFont(None, 32, bold=True)
        small = pygame.font.SysFont(None, 26)

        title = title_font.render("PARTY", True, (255,255,255))
        screen.blit(title, (SW//2 - title.get_width()//2, 36))

        list_x = 80
        list_y = 120
        row_h = 80
        box_w = SW - 160

        # party list
        for i, mon in enumerate(party):
            y = list_y + i * row_h
            selected = (i == self.index) and not self.action_open

            bg = (70,70,110) if selected else (40,40,70)
            pygame.draw.rect(screen, bg, (list_x, y, box_w, row_h-10), border_radius=14)
            pygame.draw.rect(screen, (255,255,255), (list_x, y, box_w, row_h-10), 2, border_radius=14)

            spr = pygame.transform.scale(mon.sprite, (56,56))
            screen.blit(spr, (list_x + 16, y + 8))

            name = mon.name + ("  (ACTIVE)" if mon is inventory.active else "")
            screen.blit(ui.render(name, True, (255,255,255)), (list_x + 92, y + 10))
            screen.blit(small.render(f"HP {mon.hp}/{mon.max_hp}", True, (220,220,220)), (list_x + 92, y + 44))

        # footer hint
        hint = small.render("UP/DOWN select • ENTER actions • ESC/BKSP back", True, (200,200,200))
        screen.blit(hint, (SW//2 - hint.get_width()//2, SH - 38))

        # action popup
        if self.action_open:
            w, h = 360, 220
            ax = SW//2 - w//2
            ay = SH//2 - h//2

            pygame.draw.rect(screen, (20,20,50), (ax, ay, w, h), border_radius=18)
            pygame.draw.rect(screen, (255,255,255), (ax, ay, w, h), 2, border_radius=18)

            t = ui.render("ACTIONS", True, (255,255,255))
            screen.blit(t, (ax + w//2 - t.get_width()//2, ay + 18))

            for i, a in enumerate(self.actions):
                col = (255,220,80) if i == self.action_index else (230,230,230)
                screen.blit(ui.render(a, True, col), (ax + 40, ay + 70 + i * 34))
