# 1. Module Imports
import pygame # Importing pygame for game development
import random # Importing random module for enemy positions and movements
import os # Importing os module to load files from assets folder

#2. Initializers
pygame.init() # This line starts the pygame module
pygame.mixer.init() # This line starts the mixer module for sound effects

# 3. Setting up the game window dimensions and title
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame. display.set_caption("Space Shooter")

# 4. Asset Loading
background = pygame.image.load(os.path.join("Assets", "Background.png")) # Loading Background Asset
background = pygame.transform.scale(background, (WIDTH, HEIGHT)) # Scaling background image to fit game window

player_img = pygame.image.load(os.path.join("Assets", "Player.png")).convert_alpha()
player_img = pygame.transform.scale(player_img, (64, 64))

# 4B. Loading sound effect
shoot_sound = pygame.mixer.Sound(os.path.join("Assets", "Retro Laser.mp3")) #Loading laser sound effect

# 4C. Loading Space Rock and UFO assets
asteroid_img = pygame.image.load(os.path.join("Assets", "Space Rock.png")).convert_alpha()
asteroid_img = pygame.transform.scale(asteroid_img, (64, 64))

UFO_img = pygame.image.load(os.path.join("Assets", "UFO.png")).convert_alpha()
UFO_img = pygame.transform.scale(UFO_img, (64, 48))

# 5. Player Setup
player_rect = player_img.get_rect()
player_rect.centerx = WIDTH // 2
player_rect.bottom = HEIGHT - 30
player_speed = 5

# 6. Scrolling Background Setup
bg_y1 = 0 
bg_y2 = -HEIGHT #Allows two copies of background to move seamlessly

#7. Laser Setup
laser_img = pygame.image.load(os.path.join("Assets", "Laser.png")).convert_alpha()
laser_img = pygame. transform.scale(laser_img, (8,24))
lasers =[] #List to hold all active lasers
laser_speed = 8 

# 8. Enemy Setup
asteroids = []
asteroid_speed = 1 
spawn_timer = 0
spawn_delay = 180 


# 9. Spawning Asteroids
def spawn_asteroid():
    asteroid_rect = asteroid_img.get_rect()
    asteroid_rect.x = random.randint(0, WIDTH - asteroid_rect.width)
    asteroid_rect.y = -64
    asteroids.append(asteroid_rect)  



# 10. Game Loop
# Adding the game loop
running = True #This runs the game loop
while running:

    #Event Handling:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False # Allows you to click "x" to close the game window

        #Shoot Laser:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                shoot_sound.play() # Play laser sound effect

                laser_rect = laser_img.get_rect()
                laser_rect.centerx = player_rect.centerx
                laser_rect.bottom = player_rect.top
                lasers.append(laser_rect) #Adding new laser to the list of active lasers
                

    #Scrolling Background Movement
    bg_y1 += 2
    bg_y2 += 2

    if bg_y1 >= HEIGHT: #Resetting background position
        bg_y1 = -HEIGHT
    if bg_y2 >= HEIGHT:
        bg_y2 = -HEIGHT # Creating Scroll loop

    # Setting up player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_rect.x += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_rect.y -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_rect.y += player_speed

    # Adding boundaries to player movement
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > WIDTH:
        player_rect.right = WIDTH
    if player_rect.top < 0:
        player_rect.top = 0
    if player_rect.bottom > HEIGHT:
        player_rect.bottom = HEIGHT

    # Moving lasers
    for laser in lasers:
        laser.y -= laser_speed

    lasers = [laser for laser in lasers if laser.bottom > 0] #Removing lasers that go off screen

    # Spawning asteroids
    spawn_timer += 1
    if spawn_timer >= spawn_delay:
        spawn_asteroid()
        spawn_timer = 0


    # Moving asteroids
    for asteroid in asteroids:
        asteroid.y += asteroid_speed
        asteroid.x += random.randint(-1, 1) # Adding slight horizontal movement to asteroids

    # Removing asteroids that go off screen
    asteroids = [a for a in asteroids if a.top < HEIGHT]

    # ----- Collision detection: lasers hit asteroids -----
    destroyed_asteroids = []
    destroyed_lasers = []
    for laser in lasers:
        for asteroid in asteroids:
            if laser.colliderect(asteroid):
                destroyed_asteroids.append(asteroid)
                destroyed_lasers.append(laser)
                break  # laser destroyed, move to next laser

    if destroyed_asteroids:
        asteroids = [a for a in asteroids if a not in destroyed_asteroids]
    if destroyed_lasers:
        lasers = [l for l in lasers if l not in destroyed_lasers]

    # Drawing player 
    screen.blit(background, (0, bg_y1)) 
    screen.blit(background, (0, bg_y2)) #Drawing scrolling background

    screen.blit(player_img, player_rect)

    #Drawing Lasers
    for laser in lasers:
        screen.blit(laser_img, laser)

    #Drawing Asteroids
    for asteroid in asteroids:
        screen.blit(asteroid_img, asteroid)



    pygame.display.update() #Updating display with new background positions
pygame.quit() 

