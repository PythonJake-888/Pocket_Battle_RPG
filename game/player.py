import pygame, os
from game.config import TILE_SIZE, SCREEN_SCALE, OVERWORLD_DIR

def load_player_sprites():
    base = os.path.join(OVERWORLD_DIR, "player")
    frames = {"down":[], "up":[], "right":[], "left":[]}

    for d in ["down","up","right"]:
        for i in range(2):
            img = pygame.image.load(f"{base}/{d}_{i}.png").convert_alpha()
            frames[d].append(img)
    for i in range(2):
        frames["left"].append(pygame.transform.flip(frames["right"][i],True,False))
    return frames

class OverworldPlayer:
    def __init__(self,x,y,frames):
        self.rect = pygame.Rect(x,y,TILE_SIZE,TILE_SIZE)
        self.frames = frames
        self.dir="down"
        self.frame=0
        self.timer=0
        self.speed=90

    def update(self,dt):
        keys=pygame.key.get_pressed()
        vx=vy=0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: vx=-1; self.dir="left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: vx=1; self.dir="right"
        if keys[pygame.K_w] or keys[pygame.K_UP]: vy=-1; self.dir="up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: vy=1; self.dir="down"

        self.rect.x+=vx*self.speed*dt
        self.rect.y+=vy*self.speed*dt

        if vx or vy:
            self.timer+=dt
            if self.timer>0.18:
                self.timer=0; self.frame=1-self.frame
        else: self.frame=0

    def draw(self,screen,camx,camy):
        img=self.frames[self.dir][self.frame]
        img=pygame.transform.scale(img,(TILE_SIZE*SCREEN_SCALE,TILE_SIZE*SCREEN_SCALE))
        screen.blit(img,(self.rect.x*SCREEN_SCALE-camx,
                          self.rect.y*SCREEN_SCALE-camy))
