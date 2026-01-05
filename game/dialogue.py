import pygame

class DialogueBox:
    def __init__(self):
        self.open = False
        self.text = ""
        self.font = pygame.font.SysFont(None, 26)
        self.big = pygame.font.SysFont(None, 30)

    def show(self, text):
        self.text = text
        self.open = True

    def close(self):
        self.open = False

    def handle(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    self.close()

    def draw(self, screen, SW, SH):
        if not self.open:
            return

        box = pygame.Surface((SW, 120))
        box.fill((20,20,20))
        pygame.draw.rect(box,(255,255,255),(0,0,SW,120),3)

        screen.blit(box, (0, SH - 120))
        screen.blit(self.big.render(self.text, True, (255,255,255)), (30, SH - 95))
