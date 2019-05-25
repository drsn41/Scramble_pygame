# Shmup game
import pygame
import random
from os import path

imgDir = path.join(path.dirname(__file__), 'img')
sndDir = path.join(path.dirname(__file__), 'snd')

WIDTH = 640
HEIGHT = 480
FPS = 30

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SHIP = (8, 33, 82)

# initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Box!")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
boxes = pygame.sprite.Group()
bullets = pygame.sprite.Group()


class Box(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, random.randrange(10, HEIGHT/2)))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.left = WIDTH
        self.rect.bottom = HEIGHT
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        self.speed_x -= 10
        self.rect.x += self.speed_x
        if self.rect.right < 0:
            self.kill()


class Ship(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(imgDir, "ship3.png"))
        # self.image.set_colorkey(SHIP)
        self.sndShoot = pygame.mixer.Sound(path.join(sndDir, 'laserShoot.wav'))
        self.sndShoot.set_volume(0.6)
        self.rect = self.image.get_rect()
        self.radius = 1
        pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = 50
        self.rect.bottom = HEIGHT / 2
        self.speedx = 0
        self.speedy = 0
        self.vel = 12
        self.fuel = 100
        self.lastUpdateTime = pygame.time.get_ticks()
        self.shootDelay = 250
        self.lastShot = pygame.time.get_ticks()

    def update(self):
        self.speedx = 0
        self.speedy = 0
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.speedx = self.vel

        if keys[pygame.K_LEFT]:
            self.speedx = -self.vel

        if keys[pygame.K_UP]:
            self.speedy = -self.vel

        if keys[pygame.K_DOWN]:
            self.speedy += self.vel

        if keys[pygame.K_SPACE]:
            self.shoot()

        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        self.rect.y += self.speedy
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.lastShot > self.shootDelay:
            self.lastShot = now
            bullet = Bullet(self.rect.right, self.rect.centery + 7)
            all_sprites.add(bullet)
            bullets.add(bullet)
            self.sndShoot.play()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.bulletImg = pygame.image.load(path.join(imgDir, "fire15.png")).convert()
        self.image = pygame.transform.scale(self.bulletImg, (15, 7))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedx = 20

    def update(self):
        self.rect.x += self.speedx
        if self.rect.left > WIDTH:
            self.kill()


def create_box():
    box = Box()
    if not boxes:
        boxes.add(box)
        all_sprites.add(box)
    else:
        box.rect.left = boxes.sprites()[-1].rect.right
        boxes.add(box)
        all_sprites.add(boxes)


draw_time = pygame.time.get_ticks()
player = Ship()
all_sprites.add(player)
# Game loop
running = True
while running:
    # keep loop running at the right speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # check for closing the window
        if event.type == pygame.QUIT:
            running = False

    time_now = pygame.time.get_ticks()
    if time_now - draw_time > 120:
        create_box()
        draw_time = time_now

    # check ship hit a mountain


    # print(len(boxes))
    all_sprites.update()
    # Draw / render
    screen.fill(BLACK)
    all_sprites.draw(screen)
    # after drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
quit()