import pygame, random
from os import path

imgDir = path.join(path.dirname(__file__),'img')
sndDir = path.join(path.dirname(__file__),'snd')

WIDTH = 500
HEIGHT = 480
FPS = 30

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0 )
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scramble Game")
clock = pygame.time.Clock()

fontName = pygame.font.match_font('arial')


def drawShieldBar(surf, x, y, pct):
    if pct < 0 :
        pct = 0
    BAR_LENGHT = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGHT
    fillRect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    outlineRect = pygame.Rect(x, y, BAR_LENGHT, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fillRect)
    pygame.draw.rect(surf, WHITE, outlineRect, 2)


def createMob():
    m = Mob()
    allSprites.add(m)
    mobs.add(m)


def drawText(surf, text ,size, x, y):
    font = pygame.font.Font(fontName, size)
    textSurface = font.render(text, True, WHITE)
    textRect = textSurface.get_rect()
    textRect.midtop = (x, y)
    surf.blit(textSurface, textRect)


class Ship(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = playerImg
        self.rect = self.image.get_rect()
        self.radius = 1
        pygame.draw.circle(self.image, RED,self.rect.center, self.radius)
        self.rect.centerx = 50
        self.rect.bottom = HEIGHT/2
        self.speedx = 0
        self.speedy = 0
        self.vel = 10
        self.fuel = 100
        self.lastUpdateTime = pygame.time.get_ticks()
        self.shield = 100
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
            bullet = Bullet(self.rect.right,self.rect.centery+7)
            allSprites.add(bullet)
            bullets.add(bullet)
            sndShoot.play()


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.imageOrig = random.choice(meteorImgs)
        self.imageOrig.set_colorkey(BLACK)
        self.image = self.imageOrig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.x = random.randrange(WIDTH, WIDTH+100)
        self.rect.y = random.randrange(0,HEIGHT - self.rect.height)
        self.speedx = random.randrange(1,8)
        self.speedy = random.randrange(-3,3)
        self.rot = 0
        self.rotSpeed = random.randrange(-8,8)
        self.lastUpdateTime = pygame.time.get_ticks()

    def rotate(self):
        timeNow = pygame.time.get_ticks()
        if timeNow - self.lastUpdateTime > 50:
            self.lastUpdateTime = timeNow
            self.rot = self.rot + self.rotSpeed % 360
            newImage = self.image = pygame.transform.rotate(self.imageOrig, self.rot)
            oldCenter = self.rect.center
            self.image = newImage
            self.rect = self.image.get_rect()
            self.rect.center = oldCenter

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x -= self.speedx
        if self.rect.right < 0 or self.rect.bottom > HEIGHT+10 or self.rect.top <0:
            self.rect.x = random.randrange(WIDTH, WIDTH + 40)
            self.rect.y = random.randrange(0, HEIGHT - self.rect.height)
            self.speedx = random.randrange(1, 8)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bulletImg,(4,4))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedx = 20

    def update(self):
        self.rect.x += self.speedx
        if self.rect.left > WIDTH:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosionAnim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.lastUpdate = pygame.time.get_ticks()
        self.frameRate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.lastUpdate > self.frameRate:
            self.lastUpdate = now
            self.frame += 1
            if self.frame == len(explosionAnim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosionAnim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


#Image Load
playerImg = pygame.image.load(path.join(imgDir,"ship3.png"))
bulletImg = pygame.image.load(path.join(imgDir,"bullet.gif")).convert()
bgImg = pygame.image.load(path.join(imgDir,"bg.gif")).convert()

meteorImgs = []
meteorList = ['meteorBrown_big1.png', 'meteorBrown_big2.png', 'meteorBrown_big3.png',
              'meteorBrown_med1.png', 'meteorBrown_med2.png', 'meteorBrown_small1.png',
              'meteorBrown_small2.png','meteorBrown_tiny1.png']
for met in meteorList:
    meteorImgs.append(pygame.image.load(path.join(imgDir, met)).convert())

explosionAnim = {}
explosionAnim['lg'] = []
explosionAnim['sm'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(imgDir,filename))#.convert()
    imgLg = pygame.transform.scale(img,(75,75))
    explosionAnim['lg'].append(imgLg)
    imgSm = pygame.transform.scale(img,(32,32))
    explosionAnim['sm'].append(imgSm)
#Sound Load
sndShoot = pygame.mixer.Sound(path.join(sndDir, 'laserShoot.wav'))
sndShoot.set_volume(0.4)
sndExplosion = pygame.mixer.Sound(path.join(sndDir, 'explosion.wav'))
sndExplosion.set_volume(0.5)
        #pygame.mixer.music(path.join(sndDir, 'sndBackground.waw'))
        #pygame.mixer.music.set_volume(0.4)
#Groups Sprite
bgRect = bgImg.get_rect()
allSprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Ship()
allSprites.add(player)
for i in range(8):
    createMob()

score = 0
        #pygame.mixer.music.play(loops=-1)
running = True
while running:

    clock.tick(FPS)
    timeNow = pygame.time.get_ticks()
    if timeNow - player.lastUpdateTime > 180:
        player.fuel -= 1
        player.lastUpdateTime = timeNow
    if player.fuel <= 0:
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    #Update
    allSprites.update()
    #check bullet hit a mob
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        sndExplosion.play()
        score += 100 - hit.radius
        exp = Explosion(hit.rect.center,'sm')
        allSprites.add(exp)
        createMob()
    #check mob hit player
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        sndExplosion.play()
        exp = Explosion(hit.rect.center, 'lg')
        allSprites.add(exp)
        player.shield -= hit.radius *2
        if player.shield <= 0:
            running = False

    #Draw / Render
    screen.fill(BLACK)
    allSprites.draw(screen)
    drawText(screen, "Score: " + str(score), 18, HEIGHT/2, 10)
    drawText(screen, "Fuel: " + str(player.fuel), 18, HEIGHT/3, 10)
    drawShieldBar(screen, 0, 0, player.shield)

    #after drawing everything flip the display
    pygame.display.flip()

pygame.quit()


