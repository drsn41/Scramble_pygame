import pygame, random
from os import path

imgDir = path.join(path.dirname(__file__),'img')
sndDir = path.join(path.dirname(__file__),'snd')

WIDTH = 640
HEIGHT = 480
FPS = 30

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BRIGHT_RED = (255,0,0)
BRIGHT_GREEN = (0,255,0)
HS_FILE = "highscore.txt"
TITLE = "Scramble!"


class Label(pygame.sprite.Sprite):
    def __init__(self, fontName="freesansbold.ttf"):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(fontName, 20)
        self.text = ""
        self.fgColor = ((0x00, 0x00, 0x00))
        self.bgColor = ((0xFF, 0xFF, 0xFF))
        self.center = (100, 100)
        self.size = (150, 30)

    def update(self):
        self.image = pygame.Surface(self.size)
        self.image.fill(self.bgColor)
        fontSurface = self.font.render(self.text, True, self.fgColor, self.bgColor)
        # center the text
        xPos = (self.image.get_width() - fontSurface.get_width()) / 2

        self.image.blit(fontSurface, (xPos, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self.center


class Button(Label):
    def __init__(self):
        Label.__init__(self)
        self.active = False
        self.clicked = False
        self.bgColor = (0xCC, 0xCC, 0xCC)

    def update(self):
        Label.update(self)

        self.clicked = False
        # check for mouse input
        if pygame.mouse.get_pressed() == (1, 0, 0):
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.active = True

        # check for mouse release
        if self.active == True:
            if pygame.mouse.get_pressed() == (0, 0, 0):
                self.active = False
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    self.clicked = True


class Ship(pygame.sprite.Sprite):
    def __init__(self, all_sprites, bullets):
        self.all_sprite = all_sprites
        self.bullets = bullets
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
            self.shoot(self.all_sprite,self.bullets)

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

    def shoot(self,all_sprites, bullets):
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


class Fuel(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.sndFuelUp = pygame.mixer.Sound(path.join(sndDir, 'sfx_shieldUp.ogg'))
        self.image = pygame.image.load(path.join(imgDir, 'fuel.png'))
        #self.image.set_colorkey((50, 132, 186))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedx = 5

    def update(self):
        self.rect.x -= self.speedx
        if self.rect.right < 0:
            self.kill()


class Mob(pygame.sprite.Sprite):
    def __init__(self, level, ys, ye):
        pygame.sprite.Sprite.__init__(self)
        self.level = level
        self.ys = ys
        self.ye = ye
        self.meteorImgs = []
        self.meteorList = ['meteorBrown_big1.png', 'meteorBrown_big2.png', 'meteorBrown_big3.png',
                           'meteorBrown_med1.png', 'meteorBrown_med2.png', 'meteorBrown_small1.png',
                           'meteorBrown_small2.png', 'meteorBrown_tiny1.png']
        for met in self.meteorList:
            self.meteorImgs.append(pygame.image.load(path.join(imgDir, met)).convert())
        self.imageOrig = random.choice(self.meteorImgs)
        self.imageOrig.set_colorkey(BLACK)
        self.image = pygame.transform.scale(self.imageOrig, (17, 17))
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 /2)
        self.rect.x = random.randrange(WIDTH, WIDTH+320)
        self.rect.centery = random.randrange(self.ys, self.ye)
        self.speedx = level * 6
        self.rot = 0
        self.rotSpeed = random.randrange(3, 8)
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
        #self.rect.y += self.speedy
        self.rect.x -= self.speedx
        if self.rect.right < 0 or self.rect.bottom > HEIGHT+10 or self.rect.top < 0:
            self.rect.x = random.randrange(WIDTH, WIDTH + 320)
            self.rect.centery = random.randrange(self.ys, self.ye)
            self.speedx = self.level * 6


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
        self.image = pygame.image.load(path.join(imgDir,"bg.gif")).convert()
        self.rect = self.image.get_rect()
        self.dx = 5
        self.reset()

    def update(self):
        self.rect.right -= self.dx
        if self.rect.right <= 640:
            self.reset()

    def reset(self):
        self.rect.right = 1920


class Box(pygame.sprite.Sprite):
    def __init__(self, max_length, base_cor):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, random.randrange(10, max_length)))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.left = WIDTH

        if base_cor == 35:
            self.rect.top = base_cor
        else:
            self.rect.bottom = base_cor

        self.speed_x = 0
        self.draw_time = 0

    def update(self):
        self.speed_x = 0
        self.speed_x -= 6
        self.rect.x += self.speed_x
        if self.rect.right <= 0:
            self.kill()


class Game:
    def __init__(self):
        # initialize game window, etc
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font_name = pygame.font.match_font('arial')
        self.running = True
        self.level = 1
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.load_data()

    def new(self):
        # start a new game
        self.score = 0
        self.lives = 5
        self.boxes = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.fuels = pygame.sprite.Group()
        self.player = Ship(self.all_sprites, self.bullets)
        self.space = Space()
        self.all_sprites.add(self.space)
        self.all_sprites.add(self.player)
        self.run()

    def load_data(self):
        # load high score
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

    def create_box(self, max_length, base_cor):
        box = Box(max_length, base_cor)
        if not self.boxes:
            self.boxes.add(box)
            self.all_sprites.add(box)
        else:
            box.rect.left = self.boxes.sprites()[-1].rect.right
            self.boxes.add(box)
            self.all_sprites.add(box)
        if len(self.boxes) > 40:
            self.boxes.sprites()[-1].kill()

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def create_mob(self, level, ys, ye):
        mob = Mob(level, ys, ye)
        self.all_sprites.add(mob)
        self.mobs.add(mob)

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

    def run(self):
        # Game Loop
        self.playing = True
        for i in range(8):
            self.create_mob(self.level, ys=0, ye=270)
        draw_time = pygame.time.get_ticks()
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()

    def events(self):
        # Game Loop - events
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

        time_now = pygame.time.get_ticks()

        if self.score > 4000:
            self.level = 2

        if self.score > 8000:
            self.level = 3

        if self.level == 1:
            self.create_box(180, 454)

        if self.level == 2:
            self.player.vel = 14
            if random.random() > 0.90:
                self.create_box(160, 35)
            else:
                self.create_box(150, 454)
        if self.level == 3:
            self.player.vel = 16
            if random.random() > 0.50:
                self.create_box(160, 35)
            else:
                self.create_box(180, 454)

        if time_now - self.player.lastUpdateTime > 300:
            self.player.fuel -= self.level
            self.player.lastUpdateTime = time_now

        if self.player.fuel <= 0:
            self.playing = False

        # check player hit a powerup
        hits = pygame.sprite.spritecollide(self.player,self.fuels, True)
        for hit in hits:
            hit.sndFuelUp.play()
            if self.level == 1:
                self.player.fuel += random.randrange(10, 20)
            if self.level == 2:
                self.player.fuel += random.randrange(20, 40)
            if self.level == 3:
                self.player.fuel += random.randrange(30, 60)
            if self.player.fuel >= 100:
                self.player.fuel = 100

        # check mob hit player
        hits = pygame.sprite.spritecollide(self.player, self.boxes, False, pygame.sprite.collide_circle)
        for hit in hits:
            exp = Explosion(hit.rect.center, 'lg')
            exp.sndExplosion.play()
            self.all_sprites.add(exp)
            self.player.kill()
            self.lives -= 1
            if self.lives <= 0:
                self.playing = False
            self.player = Ship(self.all_sprites,self.bullets)
            self.all_sprites.add(self.player)

        # check bullet hit a mob
        hits = pygame.sprite.groupcollide(self.mobs, self.bullets, True, True)
        for hit in hits:
            exp = Explosion(hit.rect.center, 'sm')
            exp.sndExplosion.play()
            self.score += 100*self.level - hit.radius
            self.all_sprites.add(exp)
            if random.random() > (0.97 - (self.level*0.07)):
                fuel = Fuel(hit.rect.center)
                self.all_sprites.add(fuel)
                self.fuels.add(fuel)
            if self.level == 1:
                self.create_mob(self.level, ys=0, ye=270)
            if self.level == 2:
                self.create_mob(self.level, ys=155, ye=300)
            if self.level == 3:
                self.create_mob(self.level, ys=155, ye=300)

        # check bullet hit a box
        hits = pygame.sprite.groupcollide(self.bullets, self.boxes, True, False)
        for hit in hits:
            exp = Explosion(hit.rect.center, 'sm')
            exp.sndExplosion.play()
            self.all_sprites.add(exp)

        # check mob hit player
        hits = pygame.sprite.spritecollide(self.player, self.mobs, True, pygame.sprite.collide_circle)
        for hit in hits:
            exp = Explosion(hit.rect.center, 'lg')
            exp.sndExplosion.play()
            self.all_sprites.add(exp)
            self.lives -= 1
            if self.lives <= 0:
                self.playing = False

    def draw(self):
        # Game Loop - draw
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.draw_text("Points:"+str(self.score), 22, WHITE, WIDTH / 2, 10)
        self.draw_text("Ships: "+str(self.lives), 22, WHITE, WIDTH / 2 - 100, 10)
        self.draw_text("Level: " + str(self.level), 22, WHITE, WIDTH / 2 - 200, 10)
        self.draw_text("FUEL", 22, WHITE, 95, 454)
        self.draw_live_bar(self.screen, 120, 456, self.player.fuel)
        # *after* drawing everything, flip the display
        pygame.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        pygame.mixer.music.load(path.join(sndDir, 'Yippee.ogg'))
        pygame.mixer.music.play(loops=-1)
        self.screen.fill(BLACK)

        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, 30)
        self.draw_text("Arrows to move, Space to Fire", 22, WHITE, WIDTH / 2, 80)
        self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, 100)
        self.draw_text("Choose a level to play", 22, WHITE, WIDTH / 2, 120)
        self.draw_text("or Play Arcade", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("Level 1", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 7)
        self.draw_text("Level 2", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 6)
        self.draw_text("Level 3", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 5)


        self.btn_play = Button()
        self.btn_play.bgColor = (0, 255, 0)
        self.btn_play.font = pygame.font.Font("goodfoot.ttf", 30)
        self.btn_play.center = (200, 420)
        self.btn_play.size = (100, 50)
        self.btn_play.text = "Play"

        self.btn_quit = Button()
        self.btn_quit.bgColor = (255, 0, 0)
        self.btn_quit.font = pygame.font.Font("goodfoot.ttf", 30)
        self.btn_quit.center = (420, 420)
        self.btn_quit.size = (100, 50)
        self.btn_quit.text = "Quit"

        self.screen_sprites = pygame.sprite.Group()
        self.screen_sprites.add(self.btn_play)
        self.screen_sprites.add(self.btn_quit)
        self.screen_sprites.update()
        self.screen_sprites.draw(self.screen)

        pygame.display.flip()
        self.wait_for_key(self.btn_play, self.btn_quit, self.screen_sprites)
        pygame.mixer.music.fadeout(500)

    def wait_for_key(self, btn_play, btn_quit, screen_sprites):
        waiting = True
        while waiting:
            pygame.time.delay(100)
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.playing = False
                    self.running = False
                    waiting = False
            if btn_play.clicked:
                self.all_sprites.empty()
                self.new()
                waiting = False
            if btn_quit.clicked:
                self.playing = False
                self.running = False
                waiting = False
            screen_sprites.update()

    def show_go_screen(self):
        # game over/continue
        if not self.running:
            return
        pygame.mixer.music.load(path.join(sndDir, 'Yippee.ogg'))
        pygame.mixer.music.play(loops=-1)
        self.btn_play.text = "Restart"
        self.level = 1
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)

        self.draw_text("Try Again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)

        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            self.draw_text(str(self.score), 30, WHITE, WIDTH / 2, HEIGHT / 2)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)

        self.screen_sprites.update()
        self.screen_sprites.draw(self.screen)

        pygame.display.flip()
        self.wait_for_key(self.btn_play, self.btn_quit, self.screen_sprites)
        pygame.mixer.music.fadeout(500)


def main():
    g = Game()
    g.show_start_screen()
    while g.running:
        g.show_go_screen()

    pygame.quit()
    quit()


if __name__ == "__main__":
    main()





