import pygame
import os
import time
import random
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader")
global move_counter
move_counter = 0


# Load sounds
shoot_sound = pygame.mixer.Sound(os.path.join("sounds", "laser_shoot.mp3"))
death_sound = pygame.mixer.Sound(os.path.join("sounds", "death.mp3"))
damage_sound = pygame.mixer.Sound(os.path.join("sounds", "Damage_sound.mp3"))

# Load images
Enemy1_SPACE_SHIP = pygame.image.load(os.path.join("images", "enemy_1.png"))
Enemy2_SPACE_SHIP = pygame.image.load(os.path.join("images", "enemy_2.png"))
Enemy3_SPACE_SHIP = pygame.image.load(os.path.join("images", "enemy_3.png"))

# Player ship
PLAYER_SPACE_SHIP = pygame.image.load(os.path.join("images", "Spaceship_player.png"))  

# Lasers
Enemy1_LASER = pygame.image.load(os.path.join("images", "laser_blue.png"))
Enemy2_LASER = pygame.image.load(os.path.join("images", "laser_orange.png"))
Enemy3_LASER = pygame.image.load(os.path.join("images", "laser_green.png"))
PLAYER_LASER = pygame.image.load(os.path.join("images", "laser_red.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("images", "background_main.png")), (HEIGHT,WIDTH ))

class Laser:
    def __init__(self, x, y, img): # Laser constructor
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    
    def __init__(self, x, y, health=100): # Ship constructor
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
        
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj): # Laser movment at all ships
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                damage_sound.play()
                self.lasers.remove(laser)

    def cooldown(self): 
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0

        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            shoot_sound.play() # shoot sound
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):

    COOLDOWN = 20 

    def __init__(self, x, y, health=100): # constructor
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SPACE_SHIP
        self.laser_img = PLAYER_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs): # lasers movment
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        global score 
                        score += 10
                        death_sound.play() # Sound when an enemy ship is destroyed
                        objs.remove(obj)
                        self.lasers.remove(laser)
                        

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))

class Enemy(Ship): # Three types of enemy ships
    COLOR_MAP = {
        "silver": (Enemy1_SPACE_SHIP, Enemy1_LASER),
        "red": (Enemy2_SPACE_SHIP, Enemy2_LASER),
        "green": (Enemy3_SPACE_SHIP, Enemy3_LASER)
    }

    def __init__(self, x, y, color, health=100): # constructor
        super().__init__(x, y, health) 
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.COOLDOWN = random.randrange(10, 60) # random shot frequency

    def move(self, vel,):

        global move_counter
        move_counter += 1
        
        if level % 2 == 0:
            if move_counter < 200:
                dir_x = 0
            elif move_counter <400:
                dir_x = -3
            elif move_counter < 600 :
                dir_x = 3
            else:
                move_counter = 0
                dir_x = 0
        else:
            dir_x = 0

        self.y += vel  
        if (self.x + dir_x < WIDTH) and (self.x +dir_x > 0):
                self.x += dir_x 

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2): # Defining hit
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    global level
    level = 0
    lives = 5
    global score
    score = 0

    main_font = pygame.font.SysFont("comicsans", 30)
    lost_font = pygame.font.SysFont("comicsans", 60)


    # Background music
    pygame.mixer.music.load(os.path.join("sounds", "Accelerated.mp3"))
    pygame.mixer.music.play(loops=-1)

    enemies = []
    wave_length = 2 # basic number of enemies 
    enemy_vel = 1 # Enemy ship speed

    player_vel = 5 # Player ship speed
    laser_vel = 8 # Laser speed

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        score_label = main_font.render(f"Score: {score}", 1, (255,255,255))

        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (10,725))
        
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!", 1, (255, 255, 255)) # Text You Lost
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350)) # Text center
    
        pygame.display.update()

    while run:
        clock.tick(FPS)

        redraw_window()   

        if lives <= 0 or player.health <= 0: # Level completion condition 
            lost = True
            lost_count += 1

        if lost: # Continue or Quit option
            if lost_count > FPS * 5:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 4 # 4 more enemies per level
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["silver", "red", "green"])) # spawning enemy ships
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed() # controls
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]: # shoot
            player.shoot()

        for enemy in enemies[:]: # enemy movment
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
           
            if random.randrange(0, 2*60) == 1: # enemy fire rate
               enemy.shoot()

            if collide(enemy, player): # Collide player with enemy
                player.health -= 10
                score -= 15
                death_sound.play()
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT: # lives counter down
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Press the mouse to begin!", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
              main()

    pygame.quit()               

main_menu()          