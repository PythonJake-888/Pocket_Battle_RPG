import pygame

class PauseMenu:
    def __init__(self):
        self.open = False
        self.cursor = 0
        self.options = ["RESUME", "BAG", "PARTY", "QUIT"]

    def toggle(self):
        self.open = not self.open

    def handle(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:

                if e.key in (pygame.K_UP, pygame.K_w):
                    self.cursor = (self.cursor - 1) % len(self.options)

                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.cursor = (self.cursor + 1) % len(self.options)

                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    choice = self.options[self.cursor]

                    if choice == "RESUME":
                        self.open = False

                    elif choice == "PARTY":
                        # 🔥 Tell overworld to open party menu
                        return "party"

                    elif choice == "QUIT":
                        pygame.quit()
                        exit()


    def draw(self, screen, w, h):
        panel = pygame.Surface((300, 240))
        panel.fill((25, 25, 60))
        pygame.draw.rect(panel,(255,255,255),(0,0,300,240),3)

        font = pygame.font.SysFont(None,36)
        for i,opt in enumerate(self.options):
            col = (255,255,0) if i==self.cursor else (230,230,230)
            panel.blit(font.render(opt,True,col),(60,50+i*45))

        screen.blit(panel,(w//2-150,h//2-120))
