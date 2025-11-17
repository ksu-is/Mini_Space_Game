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
player_img = pygame.transform.scale(player_img, (96, 96))

# 4B. Loading sound effect
shoot_sound = pygame.mixer.Sound(os.path.join("Assets", "Retro Laser.mp3")) #Loading laser sound effect
# Load UFO explosion sound (handle potential filename misspelling)
ufo_sound = None
for name in ("UFO Explosion.mp3", "UFO Exploision.mp3", "ufo_explosion.mp3"):
    path = os.path.join("Assets", name)
    if os.path.exists(path):
        try:
            ufo_sound = pygame.mixer.Sound(path)
            break
        except Exception:
            ufo_sound = None
            break

# 4C. Loading Space Rock and UFO assets
asteroid_img = pygame.image.load(os.path.join("Assets", "Space Rock.png")).convert_alpha()
asteroid_img = pygame.transform.scale(asteroid_img, (64, 64))

UFO_img = pygame.image.load(os.path.join("Assets", "UFO.png")).convert_alpha()
UFO_img = pygame.transform.scale(UFO_img, (48, 48))

# Explosion asset (shown when asteroid is destroyed)
explosion_img = pygame.image.load(os.path.join("Assets", "Explosion.gif")).convert_alpha()
explosion_img = pygame.transform.scale(explosion_img, (96, 96))
# Large explosion for bigger enemies (UFOs) - much bigger and more visible
explosion_large_img = pygame.transform.scale(explosion_img, (320, 320))

# Make the black background of the explosion images transparent so they don't cover other sprites
# Some GIFs don't include proper alpha; using a color key for black (0,0,0) will remove the black border.
explosion_img.set_colorkey((0, 0, 0))
explosion_large_img.set_colorkey((0, 0, 0))

# Spaceship-specific explosion (used when player is hit)
# Load a dedicated spaceship explosion GIF (if present) for better visuals
if os.path.exists(os.path.join("Assets", "Spaceship Explosion.gif")):
    spaceship_explosion_img = pygame.image.load(os.path.join("Assets", "Spaceship Explosion.gif")).convert_alpha()
    spaceship_explosion_img = pygame.transform.scale(spaceship_explosion_img, (200, 200))
else:
    # fallback to generic explosion scaled
    spaceship_explosion_img = pygame.transform.scale(explosion_img, (160, 160))
spaceship_explosion_img.set_colorkey((0, 0, 0))

# UFO-specific explosion: prefer a dedicated file if present, otherwise make a large fallback
ufo_explosion_img = None
ufo_png = os.path.join("Assets", "UFO Explosion.png")
ufo_gif = os.path.join("Assets", "UFO Explosion.gif")
if os.path.exists(ufo_png):
    ufo_explosion_img = pygame.image.load(ufo_png).convert_alpha()
    ufo_explosion_img = pygame.transform.scale(ufo_explosion_img, (320, 320))
elif os.path.exists(ufo_gif):
    ufo_explosion_img = pygame.image.load(ufo_gif).convert_alpha()
    ufo_explosion_img = pygame.transform.scale(ufo_explosion_img, (320, 320))
else:
    # fallback to an even larger scaled version of the generic large explosion
    ufo_explosion_img = pygame.transform.scale(explosion_img, (360, 360))
ufo_explosion_img.set_colorkey((0, 0, 0))

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
laser_img = pygame.transform.scale(laser_img, (16, 48))
lasers =[] #List to hold all active lasers
laser_speed = 8 

# 8. Enemy Setup
asteroids = []
asteroid_speed = 1 
spawn_timer = 0
spawn_delay = 180 

# Explosions list stores ongoing explosion effects (rect + timer)
explosions = []
# UFOs
ufos = []
ufo_speed = 2
ufo_spawn_timer = 0
ufo_spawn_delay = 600

# Game state
game_over = False
player_dead = False
player_explosion_duration = 36  # frames the ship explosion plays before game over

# Fonts for UI
font = pygame.font.SysFont(None, 72)
small_font = pygame.font.SysFont(None, 36)

def reset_game():
    """Reset game state to start a new run."""
    global asteroids, ufos, lasers, explosions
    global spawn_timer, ufo_spawn_timer, bg_y1, bg_y2, game_over
    global player_dead

    asteroids = []
    ufos = []
    lasers = []
    explosions = []

    spawn_timer = 0
    ufo_spawn_timer = 0

    bg_y1 = 0
    bg_y2 = -HEIGHT

    # Reset player position
    player_rect.centerx = WIDTH // 2
    player_rect.bottom = HEIGHT - 30

    game_over = False
    player_dead = False


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
            if event.key == pygame.K_SPACE and not game_over:
                shoot_sound.play() # Play laser sound effect

                laser_rect = laser_img.get_rect()
                laser_rect.centerx = player_rect.centerx
                laser_rect.bottom = player_rect.top
                lasers.append(laser_rect) #Adding new laser to the list of active lasers
            # If game over, allow restart/quit keys handled later
                

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

    # Spawning UFOs occasionally
    ufo_spawn_timer += 1
    if ufo_spawn_timer >= ufo_spawn_delay:
        # spawn a UFO near the top
        ufo_rect = UFO_img.get_rect()
        ufo_rect.x = random.randint(0, WIDTH - ufo_rect.width)
        ufo_rect.y = -ufo_rect.height
        ufos.append(ufo_rect)
        ufo_spawn_timer = 0


    # Moving asteroids
    for asteroid in asteroids:
        asteroid.y += asteroid_speed
        asteroid.x += random.randint(-1, 1) # Adding slight horizontal movement to asteroids

    # Moving UFOs
    for ufo in ufos:
        ufo.y += ufo_speed
        ufo.x += random.randint(-1, 1)

    # Removing asteroids and ufos that go off screen
    asteroids = [a for a in asteroids if a.top < HEIGHT]
    ufos = [u for u in ufos if u.top < HEIGHT]
    # ----- Collision detection: lasers hit asteroids -----
    # When a laser hits an asteroid, spawn an explosion at the asteroid's center
    # and remove both the laser and the asteroid.
    destroyed_asteroids = []
    destroyed_lasers = []
    explosion_duration = 18  # frames to show explosion

    for laser in lasers:
        for asteroid in asteroids:
            if laser.colliderect(asteroid):
                # create explosion rect centered on asteroid (small explosion)
                exp_rect = explosion_img.get_rect()
                exp_rect.center = asteroid.center
                explosions.append({"rect": exp_rect, "timer": explosion_duration, "img": explosion_img})

                destroyed_asteroids.append(asteroid)
                destroyed_lasers.append(laser)
                break  # laser destroyed, move to next laser

    # Check laser collisions with UFOs (spawn larger explosion)
    destroyed_ufos = []
    for laser in lasers:
        for ufo in ufos:
            if laser.colliderect(ufo):
                # create a much larger explosion for UFOs using the UFO-specific image and nudge upward
                exp_rect = ufo_explosion_img.get_rect()
                exp_rect.center = (ufo.centerx, ufo.centery - 28)
                # Play UFO explosion sound if available
                if ufo_sound:
                    try:
                        ufo_sound.play()
                    except Exception:
                        pass
                # longer duration for UFO explosion
                explosions.append({"rect": exp_rect, "timer": int(explosion_duration * 3.5), "img": ufo_explosion_img})
                destroyed_ufos.append(ufo)
                destroyed_lasers.append(laser)
                break

    if destroyed_ufos:
        ufos = [u for u in ufos if u not in destroyed_ufos]

    if destroyed_asteroids:
        asteroids = [a for a in asteroids if a not in destroyed_asteroids]
    if destroyed_lasers:
        lasers = [l for l in lasers if l not in destroyed_lasers]

    # Check collisions between player and asteroids/UFOs -> game over
    # Use smaller hitboxes for asteroids and UFOs for fairer collision
    for asteroid in asteroids:
        asteroid_hitbox = asteroid.inflate(-20, -20)  # shrink by 20px each side
        if player_rect.colliderect(asteroid_hitbox) and not player_dead:
            # spawn ship explosion and mark player dead; nudge explosion upward so it centers visually
            exp_rect = spaceship_explosion_img.get_rect()
            exp_rect.center = (player_rect.centerx, player_rect.centery - 12)
            explosions.append({"rect": exp_rect, "timer": player_explosion_duration, "img": spaceship_explosion_img})
            player_dead = True
            break
    for ufo in ufos:
        ufo_hitbox = ufo.inflate(-12, -12)  # shrink by 12px each side
        if player_rect.colliderect(ufo_hitbox) and not player_dead:
            exp_rect = spaceship_explosion_img.get_rect()
            exp_rect.center = (player_rect.centerx, player_rect.centery - 12)
            explosions.append({"rect": exp_rect, "timer": player_explosion_duration, "img": spaceship_explosion_img})
            player_dead = True
            break

    # Drawing player 
    screen.blit(background, (0, bg_y1)) 
    screen.blit(background, (0, bg_y2)) #Drawing scrolling background

    # Only draw the player sprite if they're not dead (exploding)
    if not player_dead:
        screen.blit(player_img, player_rect)

    #Drawing Lasers
    for laser in lasers:
        screen.blit(laser_img, laser)

    #Drawing Asteroids
    for asteroid in asteroids:
        screen.blit(asteroid_img, asteroid)

    # Drawing UFOs
    for ufo in ufos:
        screen.blit(UFO_img, ufo)

    # Draw and update explosions (show on top of asteroids)
    new_explosions = []
    for e in explosions:
        # draw the explosion using its stored image to keep sizes correct
        img = e.get("img", explosion_img)
        screen.blit(img, e["rect"])
        e["timer"] -= 1
        if e["timer"] > 0:
            new_explosions.append(e)
        else:
            # if this was the last ship-explosion, mark game_over
            if img == spaceship_explosion_img:
                game_over = True
    explosions = new_explosions



    # If game over, display game over screen and wait for restart or quit
    if game_over:
        # darken background
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        go_text = font.render("GAME OVER", True, (255, 30, 30))
        go_rect = go_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
        screen.blit(go_text, go_rect)

        instr_text = small_font.render("Press R to restart or Q/Esc to quit", True, (255, 255, 255))
        instr_rect = instr_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
        screen.blit(instr_text, instr_rect)

        pygame.display.update()
        # Wait for input events to restart or quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    running = False
        # skip rest of loop while waiting
        continue

    pygame.display.update() #Updating display with new background positions
pygame.quit() 

