import pygame
import random
import os

'''
Variables
'''

pygame.init()
pygame.font.init()
crash_sound = pygame.mixer.Sound(os.path.join('sounds', 'crash.wav'))
run_sound = pygame.mixer.Sound(os.path.join('sounds', 'run.wav'))
jump_sound = pygame.mixer.Sound(os.path.join('sounds', 'boing.wav'))
pygame.mixer.music.load(os.path.join('sounds', 'music.wav'))
play_sound = True
worldx = 1920
worldy = 1080
fps = 60
ani = 6
world = pygame.display.set_mode((worldx, worldy), pygame.FULLSCREEN)

forwardx = 600
backwardx = 230
space_between_level = 158
block_font = pygame.font.SysFont('Arial', 18)

'''
Objects
'''

# x location, y location, img width, img height, img file
class Platform(pygame.sprite.Sprite):
    def __init__(self, xloc, yloc, imgw, imgh, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('images', img))
        self.rect = self.image.get_rect()
        self.rect.y = yloc
        self.rect.x = xloc
        self.originy = yloc
        self.originx = xloc
        self.topshake = yloc - 25
        self.mask = pygame.mask.from_surface(self.image)
        self.shaked = 0
        self.shaking = False
        self.inshake = False
        self.shakevel = -15
        self.level = random.randrange(2,7)

    def draw_level(self):
        block_level = block_font.render(f"{self.level}", 1, (255, 255, 255))
        rect = block_level.get_rect()
        world.blit(block_level, (self.rect.left + round((self.rect.width - rect.width) / 2), self.rect.top + round((self.rect.height - rect.height) / 2)))

    def shake(self):
        if self.inshake:
            self.rect.top += self.shakevel
            if self.shakevel < 0:
                if self.rect.top <=  self.topshake:
                    self.shakevel = abs(self.shakevel)

            if self.shakevel > 0:
                if self.rect.top >= self.originy:
                    self.level -= 1
                    self.shakevel = abs(self.shakevel)*-1
                    self.rect.top = self.originy
                    self.inshake = False
                    self.shaking = False

    def draw(self):
        if self.level <= 0:
            plat_list.remove(self)

        if self.shaking:
            if not self.inshake:
                self.inshake = True
            self.shake()

        world.blit(self.image, (self.rect.left, self.rect.top))
        self.draw_level()


class Player(pygame.sprite.Sprite):
    """
    Spawn a player
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0.0
        self.movey = 50.0
        self.frame = 0
        self.health = 10
        self.is_jumping = False
        self.is_falling = True
        self.images = []
        for i in range(1, 7):
            img = pygame.image.load(os.path.join('images', 'Walk' + str(i) + '.png'))
            self.images.append(img)
            self.image = self.images[0]
            self.rect = self.image.get_rect()

    def gravity(self):
        if self.is_jumping:
            self.movey += 3.2

    def control(self, x, y):
        """
        control player movement
        """
        self.movex += x

    def jump(self):
        if not self.is_jumping:
            self.is_falling = False
            self.is_jumping = True

    def draw_level(self):
        level_font = pygame.font.Font(os.path.join('fonts','Grinched 2.0.ttf'), 70)
        player_level = level_font.render(f"health : {str(self.health)}", 1, (0, 0, 0))
        world_rect = world.get_rect()
        world.blit(player_level, (world_rect.left + 25, world_rect.top + 25))  
        level_font = pygame.font.Font(os.path.join('fonts','Grinched 2.0.ttf'), 66)
        player_level = level_font.render(f"health : {str(self.health)}", 1, (255, 255, 255))
        world.blit(player_level, (world_rect.left + 27, world_rect.top + 26))

    def update(self):
        """
        Update sprite position
        """
        collision = False

        # moving left
        if self.movex < 0:
            self.frame += 1
            if self.frame > 5 * ani:
                self.frame = 0
            self.image = pygame.transform.flip(self.images[self.frame // ani], True, False)

        # moving right
        if self.movex > 0:
            self.frame += 1
            if self.frame > 5 * ani:
                self.frame = 0
            self.image = self.images[self.frame // ani]

        # collisions

        ground_hit_list = pygame.sprite.spritecollide(self, ground_list, False)
        for g in ground_hit_list:
            self.rect.bottom = g.rect.top
            self.is_falling = False  # stop jumping
            self.is_jumping = False
            self.movey = 0.0

        plat_hit_list = pygame.sprite.spritecollide(self, plat_list, False)
        if len(plat_hit_list) > 0:
            collision = True
            for p in plat_hit_list:
                if self.rect.bottom <= (p.rect.top + (p.rect.height / 2)):
                    self.rect.top = p.rect.top - self.rect.height
                    self.is_jumping = False
                    self.is_falling = False
                    self.movey = 0
                else:
                    if self.rect.top >= p.rect.bottom - (p.rect.height / 2) and not p.shaking:
                        if not p.inshake:
                            collision = False
                            pygame.mixer.Sound.play(crash_sound)
                            self.is_falling = True
                            self.movey = 14
                            p.shaking = True
        else:
            if not self.is_falling and not self.is_jumping and len(ground_hit_list) == 0:
                self.rect.y += 10
                below_list = pygame.sprite.spritecollide(self, plat_list, False)
                below_list2 = pygame.sprite.spritecollide(self, ground_list, False)
                self.rect.y -= 10.0
                if len(below_list) == 0 and len(below_list2) == 0:
                    self.movey = 15.0
                    self.is_falling = True
        
        enemy_hit_list = pygame.sprite.spritecollide(self, enemy_list, False)
        for enemy in enemy_hit_list:
            self.health -= 1
            # print(self.health)

        """
        # fall off the world
        if self.rect.y > worldy:
            self.health -= 1
            print(self.health)
            self.rect.x = tx
            self.rect.y = ty

        """
        if not collision:
            if self.is_jumping and not self.is_falling:
                self.is_falling = True
                self.movey -= 33  # how high to jump

        self.rect.left += self.movex
        self.rect.top += self.movey

        if self.movey == 0:
            self.is_falling = False

        # print ('is_falling : {} is_jumping {}  movey : {} movex : {}'.format(self.is_falling,self.is_jumping,self.movey, self.movex))


class Enemy(pygame.sprite.Sprite):
    """
    Spawn an enemy
    """

    def __init__(self, x, y, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('images', img))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.counter = 0

    def move(self):
        """
        enemy movement
        """
        distance = 80
        speed = 8

        if 0 <= self.counter <= distance:
            self.rect.x += speed
        elif distance <= self.counter <= distance * 2:
            self.rect.x -= speed
        else:
            self.counter = 0

        self.counter += 1


class Level:
    def ground(lvl, gloc, tx, ty):
        ground_list = pygame.sprite.Group()
        i = 0
        if lvl == 1:
            while i < len(gloc):
                ground = Platform(gloc[i], worldy - ty, tx, ty, 'tile-ground.png')
                ground_list.add(ground)
                i = i + 1

        if lvl == 2:
            print("Level " + str(lvl))

        return ground_list

    def bad(lvl, eloc):
        if lvl == 1:
            enemy = Enemy(eloc[0], eloc[1], 'enemy.png')
            enemy_list = pygame.sprite.Group()
            enemy_list.add(enemy)
        if lvl == 2:
            print("Level " + str(lvl))

        return enemy_list

    # x location, y location, img width, img height, img file
    def platform(lvl, tx, ty):
        plat_list = pygame.sprite.Group()
        ploc = []
        i = 0
        if lvl == 1:
            ploc.append((200, worldy - ty - 158, 3))
            ploc.append((300, worldy - ty - 316, 3))
            ploc.append((550, worldy - ty - 158, 4))
            ploc.append((380, worldy - ty - (158 * 3) , 4))
            while i < len(ploc):
                j = 0
                while j <= ploc[i][2]:
                    plat = Platform((ploc[i][0] + (j * tx)), ploc[i][1], tx, ty, 'tile.png')
                    plat_list.add(plat)
                    j = j + 1
                i = i + 1

        if lvl == 2:
            print("Level " + str(lvl))

        return plat_list

    

'''
Setup
'''

backdrop = pygame.image.load(os.path.join('images', 'Bg.png'))
clock = pygame.time.Clock()

backdropbox = world.get_rect()
main = True

player = Player()  # spawn player
player.rect.x = 0  # go to x
player.rect.y = 30  # go to y
player_list = pygame.sprite.Group()
player_list.add(player)
steps = 10

eloc = []
eloc = [300, 0]
enemy_list = Level.bad(1, eloc)

gloc = []
tx = 64
ty = 64

i = 0
while i <= (worldx / tx) + tx:
    gloc.append(i * tx)
    i = i + 1

ground_list = Level.ground(1, gloc, tx, ty)
plat_list = Level.platform(1, tx, ty)

'''
Main Loop
'''

pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.2)
while main:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            main = False

        keys = pygame.key.get_pressed()
        keys = pygame.key.get_mods()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                pygame.mixer.Sound.play(run_sound, -1)
                player.control(-steps, 0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                pygame.mixer.Sound.play(run_sound, -1)
                player.control(steps, 0)
            if event.key == pygame.K_UP or event.key == ord('w'):
                pygame.mixer.Sound.play(jump_sound)
                player.jump()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                pygame.mixer.Sound.stop(run_sound)
                player.control(steps, 0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                pygame.mixer.Sound.stop(run_sound)
                player.control(-steps, 0)

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            print('x : {} y : {}'.format(x, y))

    # scroll the world forward
    if player.rect.x >= forwardx:
        scroll = player.rect.x - forwardx
        player.rect.x = forwardx
        for p in plat_list:
            p.rect.x -= scroll
        for e in enemy_list:  # enemy scroll
            e.rect.x -= scroll  # enemy scroll

    # scroll the world backward
    if player.rect.x <= backwardx:
        scroll = backwardx - player.rect.x
        player.rect.x = backwardx
        for p in plat_list:
            p.rect.x += scroll
        for e in enemy_list:  # enemy scroll
            e.rect.x += scroll  # enemy scroll

    world.blit(backdrop, backdropbox)
    player.draw_level()
    player.update()
    player.gravity()
    player_list.draw(world)
    enemy_list.draw(world)
    ground_list.draw(world)
    #plat_list.draw(world)
    
    for plat in plat_list:
        plat.draw()

    for e in enemy_list:
        e.move()
    
    pygame.display.flip()
    clock.tick(fps)