import pygame
import os
import time
import random
pygame.font.init()
WIDTH, HEIGHT = 750,750
WN = pygame.display.set_mode((WIDTH, HEIGHT))

BG = pygame.image.load(os.path.join("assets", "background-black.png"))
BG = pygame.transform.scale(BG, (WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

REDSS = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
YELLOWSS = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))
GREENSS = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUESS = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

REDL = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
YELLOWL = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
GREENL =  pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUEL = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    def draw(self, window):
        WN.blit(self.img, (self.x, self.y))
    def move(self, vel):
        self.y += vel
    def passed(self, height):
        return not(self.y < height and self.y >= 0)
    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cooldl = 0
    def draw(self, window):
        WN.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(WN)
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.passed(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
    def cooldown(self):
        if self.cooldl >= self.COOLDOWN:
            self.cooldl = 0
        elif self.cooldl > 0: 
            self.cooldl += 1
    def shoot(self):
        if self.cooldl == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldl = 1
    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()
    

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health=health)
        self.ship_img = YELLOWSS
        self.laser_img = YELLOWL
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.passed(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))
    def draw(self,window):
        super().draw(window)
        self.healthbar(window)
class Npc(Ship):
    COLORS = {
        "red": (REDSS, REDL),
        "green": (GREENSS, GREENL),
        "blue": (BLUESS, BLUEL)
    }
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health=health)
        self.ship_img, self.laser_img = self.COLORS[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    def move(self, vel):
        self.y += vel
    def shoot(self):
        if self.cooldl == 0:
            laser = Laser(self.x -20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldl = 1

def collide(o1, o2):
    offset_x = o2.x - o1.x
    offset_y = o2.y - o1.y
    return o1.mask.overlap(o2.mask, (int(offset_x), int(offset_y))) != None

def main() :
    run = True
    lost = False
    lost_count = 0 
    level = 0
    lives = 5
    velocity = 6
    npcs = []
    npc_vel = 1
    las_vel = 5
    wave_length = 5
    player = Player(WIDTH/2 - 50, 600)

    FPS = 60
    CLOCK = pygame.time.Clock()
    MAIN_FONT = pygame.font.SysFont("comicsans", 30)
    LOST_FONT = pygame.font.SysFont("comicsans", 60)
    def refresh():
        WN.blit(BG, (0,0))
        lives_label = MAIN_FONT.render(f"Lives: {lives}", 1, (0,255,0))
        level_label = MAIN_FONT.render(f"Level: {level}", 1, (0,255,0))

        WN.blit(lives_label, (10,10))
        WN.blit(level_label, (WIDTH - level_label.get_width() - 10,10))

        for npc in npcs:
            npc.draw(WN)

        player.draw(WN)

        if lost:
            lost_label = LOST_FONT.render(f"You Lost !", 1, (255,255,255))
            WN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()
    while run: 
        CLOCK.tick(FPS)
        refresh()
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        if len(npcs) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                npc = Npc(random.randrange(50,WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "green", "blue"]))
                npcs.append(npc)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - velocity > 0:
            player.x -= velocity
        if keys[pygame.K_d] and player.x + velocity + player.get_width() < WIDTH:
            player.x += velocity
        if keys[pygame.K_w] and player.y - velocity > 0:
            player.y -= velocity
        if keys[pygame.K_s] and player.y + velocity + player.get_height() + 20 < HEIGHT:
            player.y += velocity
        if keys[pygame.K_SPACE]:
            player.shoot()
        for npc in npcs[:]:
            npc.move_lasers(las_vel, player)
            npc.move(npc_vel)

            if random.randrange(0, 4*FPS) == 1:
                npc.shoot()

            if collide(npc, player):
                player.health -= 10
                npcs.remove(npc)
            elif npc.y + npc.get_height() > HEIGHT:
                lives -= 1
                npcs.remove(npc)
            

        player.move_lasers(-las_vel, npcs)

def main_menu():
    TITLE_FONT = pygame.font.SysFont("comicsans", 80)
    run = True
    while run:

        WN.blit(BG, (0,0))
        title_label = TITLE_FONT.render("Press mouse to begin", 1, (0,255,0))
        WN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    quit()

main_menu()
