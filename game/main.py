import pygame
from game.config import SCREEN_W, SCREEN_H, FPS
from game.overworld import Overworld

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Pocket Battle RPG")
    clock = pygame.time.Clock()

    overworld = Overworld(screen)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        events = pygame.event.get()

        for e in events:
            if e.type == pygame.QUIT:
                running = False

        overworld.handle_events(events)

        overworld.update(dt)
        overworld.draw()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
