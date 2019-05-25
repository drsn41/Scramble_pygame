import pygame, random
from os import path

imgDir = path.join(path.dirname(__file__), 'img')
sndDir = path.join(path.dirname(__file__), 'snd')

WIDTH = 640
HEIGHT = 480
FPS = 30

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Proper Game v2")
clock = pygame.time.Clock()
fontName = pygame.font.match_font('arial')

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
boxes = pygame.sprite.Group()


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


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.meteorImgs = []
        self.meteorList = ['meteorBrown_big1.png', 'meteorBrown_big2.png', 'meteorBrown_big3.png',
                           'meteorBrown_med1.png', 'meteorBrown_med2.png', 'meteorBrown_small1.png',
                           'meteorBrown_small2.png', 'meteorBrown_tiny1.png']
        for met in self.meteorList:
            self.meteorImgs.append(pygame.image.load(path.join(imgDir, met)).convert())
        self.imageOrig = random.choice(self.meteorImgs)
        self.imageOrig.set_colorkey(BLACK)
        self.image = self.imageOrig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.x = random.randrange(WIDTH, WIDTH + 100)
        self.rect.y = random.randrange(0, HEIGHT - self.rect.height)
        self.speedx = random.randrange(1, 8)
        self.speedy = random.randrange(-3, 3)
        self.rot = 0
        self.rotSpeed = random.randrange(-8, 8)
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
        if self.rect.right < 0 or self.rect.bottom > HEIGHT + 10 or self.rect.top < 0:
            self.rect.x = random.randrange(WIDTH, WIDTH + 40)
            self.rect.y = random.randrange(0, HEIGHT - self.rect.height)
            self.speedx = random.randrange(1, 8)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.explosionAnim = {}
        self.explosionAnim['lg'] = []
        self.explosionAnim['sm'] = []
        for i in range(9):
            filename = 'regularExplosion0{}.png'.format(i)
            img = pygame.image.load(path.join(imgDir, filename))  # .convert()
            imgLg = pygame.transform.scale(img, (75, 75))
            self.explosionAnim['lg'].append(imgLg)
            imgSm = pygame.transform.scale(img, (32, 32))
            self.explosionAnim['sm'].append(imgSm)
        self.size = size
        self.sndExplosion = pygame.mixer.Sound(path.join(sndDir, 'explosion.wav'))
        self.sndExplosion.set_volume(0.5)
        self.image = self.explosionAnim[self.size][0]
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
            if self.frame == len(self.explosionAnim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.explosionAnim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Space(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(imgDir, "bg.gif")).convert()
        self.rect = self.image.get_rect()
        self.dx = 5
        self.reset()

    def update(self):
        self.rect.right -= self.dx
        if self.rect.right <= 640:
            self.reset()

    def reset(self):
        self.rect.right = 1920


class Scoreboard(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.lives = 5
        self.level = 1
        self.score = 0
        self.text = ""
        self.image = ""
        self.rect = ""
        self.font = pygame.font.SysFont("None", 50)

    def update(self):
        self.text = "Ships: %d, Score: %d, Level: %d" % (self.lives, self.score, self.level)
        self.image = self.font.render(self.text, 1, (255, 255, 0))
        self.rect = self.image.get_rect()


class Box(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, random.randrange(10, HEIGHT / 2)))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.left = WIDTH
        self.rect.bottom = 454
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        self.speed_x -= 10
        self.rect.x += self.speed_x
        if self.rect.right < 0:
            self.kill()


class Game(pygame.sprite.Sprite):
    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)
        self.background = pygame.Surface(screen.get_size())
        self.background.fill((0, 0, 0))
        self.screen = screen
        self.screen.blit(self.background, (0, 0))
        self.player = Ship()
        self.space = Space()
        self.mob = Mob()
        self.scoreboard = Scoreboard()
        self.friendSprites = pygame.sprite.Group(self.space, self.player)
        self.scoreSprite = pygame.sprite.Group(self.scoreboard)

    def create_mob(self):
        self.mob = Mob()
        all_sprites.add(self.mob)
        mobs.add(self.mob)

    def draw_live_bar(self, surf, x, y, pct):
        if pct < 0:
            pct = 0
        bar_length = 400
        bar_height = 20
        fill = (pct / 100) * bar_length
        fill_rect = pygame.Rect(x, y, fill, bar_height)
        outline_rect = pygame.Rect(x, y, bar_length, bar_height)
        pygame.draw.rect(surf, GREEN, fill_rect)
        pygame.draw.rect(surf, WHITE, outline_rect, 2)

    def drawText(self, surf, text, size, x, y):
        font = pygame.font.Font(fontName, size)
        textSurface = font.render(text, True, WHITE)
        textRect = textSurface.get_rect()
        textRect.midtop = (x, y)
        surf.blit(textSurface, textRect)

    def create_box(self):
        box = Box()
        if not boxes:
            boxes.add(box)
            all_sprites.add(box)
        else:
            box.rect.left = boxes.sprites()[-1].rect.right
            boxes.add(box)
            all_sprites.add(boxes)

    def instructions(self, score):
        ship = Ship()
        space = Space()
        all_sprites = pygame.sprite.Group(space, ship)
        insFont = pygame.font.SysFont(None, 50)
        insLabels = []
        instructions = (
            "Mail Pilot.     Last score: %d" % score,
            "Instructions:  You are a mail pilot,",
            "delivering mail to the islands.",
            "",
            "Fly over an island to drop the mail,",
            "but be careful not to fly too close",
            "to the clouds. Your plane will fall ",
            "apart if it is hit by lightning too",
            "many times. Steer with the mouse.",
            "",
            "good luck!",
            "",
            "click to start, escape to quit..."
        )

        for line in instructions:
            tempLabel = insFont.render(line, 1, (255, 255, 0))
            insLabels.append(tempLabel)

        keepGoing = True
        pygame.mouse.set_visible(False)
        while keepGoing:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keepGoing = False
                    donePlaying = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    keepGoing = False
                    donePlaying = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        keepGoing = False
                        donePlaying = True

            all_sprites.update()
            all_sprites.draw(screen)

            for i in range(len(insLabels)):
                screen.blit(insLabels[i], (50, 30 * i))

            pygame.display.flip()

        pygame.mouse.set_visible(False)
        return donePlaying

    def play(self):
        for i in range(8):
            self.create_mob()
        # pygame.mixer.music(path.join(sndDir, 'sndBackground.waw'))
        # pygame.mixer.music.set_volume(0.4)
        # pygame.mixer.music.play(loops=-1)
        time_start = pygame.time.get_ticks()
        running = True
        while running:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            time_now = pygame.time.get_ticks()
            if time_now - time_start > 120:
                self.create_box()
                time_start = time_now

            if time_now - self.player.lastUpdateTime > 300:
                self.player.fuel -= 1
                self.player.lastUpdateTime = time_now

            if self.player.fuel <= 0:
                running = False

            # check mob hit player
            hits = pygame.sprite.spritecollide(self.player, boxes, False, pygame.sprite.collide_circle)
            for hit in hits:
                exp = Explosion(hit.rect.center, 'lg')
                exp.sndExplosion.play()
                all_sprites.add(exp)
                self.player.kill()
                self.scoreboard.lives -= 1
                if self.scoreboard.lives <= 0:
                    running = False
                self.player = Ship()
                self.player.rect.y = 30
                all_sprites.add(self.player)

            # check bullet hit a mob
            hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
            for hit in hits:
                exp = Explosion(hit.rect.center, 'sm')
                exp.sndExplosion.play()
                self.scoreboard.score += 100 - hit.radius
                all_sprites.add(exp)
                self.create_mob()
            # check mob hit player
            hits = pygame.sprite.spritecollide(self.player, mobs, True, pygame.sprite.collide_circle)
            for hit in hits:
                exp = Explosion(hit.rect.center, 'lg')
                exp.sndExplosion.play()
                all_sprites.add(exp)
                self.scoreboard.lives -= 1
                if self.scoreboard.lives <= 0:
                    running = False

            # Update
            all_sprites.update()
            self.friendSprites.update()
            self.scoreSprite.update()

            # Draw / Render
            self.friendSprites.draw(screen)
            self.scoreSprite.draw(screen)
            # screen.fill(BLACK)
            all_sprites.draw(screen)
            # drawText(screen, "Score: " + str(score), 18, HEIGHT / 2, 10)
            self.drawText(screen, "FUEL", 20, 95, 456)
            self.draw_live_bar(screen, 120, 456, self.player.fuel)
            # after drawing everything flip the display

            pygame.display.flip()
        return self.scoreboard.score


def main():
    done_playing = False
    score = 0
    game = Game(screen)
    while not done_playing:
        done_playing = game.instructions(score)
        if not done_playing:
            score = game.play()


if __name__ == "__main__":
    main()
