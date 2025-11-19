# 1. Module Imports
import pygame # Importing pygame for game development
import random # Importing random module for enemy positions and movements
import os # Importing os module to load files from assets folder

#2. Initializers
pygame.init() # This line starts the pygame module
pygame.mixer.init() # This line starts the mixer module for sound effects
# Frame rate control
clock = pygame.time.Clock()
FPS = 120

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

# Play background music on loop (if available)
bg_music_path = os.path.join("Assets", "Background Music.mp3")
if os.path.exists(bg_music_path):
    try:
        pygame.mixer.music.load(bg_music_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # loop indefinitely
    except Exception:
        pass

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

# Player/asteroid explosion sound (load once)
explosion_sound = None
explosion_sound_path = os.path.join("Assets", "Explosion.mp3")
if os.path.exists(explosion_sound_path):
    try:
        explosion_sound = pygame.mixer.Sound(explosion_sound_path)
    except Exception:
        explosion_sound = None

# Rock-specific explosion sound: prefer Rock Explosion names, otherwise fall back to explosion_sound
rock_sound = None
for name in ("Rock Explosion.mp3", "Rock_Explosion.mp3", "rock_explosion.mp3", "Explosion.mp3"):
    path = os.path.join("Assets", name)
    if os.path.exists(path):
        try:
            rock_sound = pygame.mixer.Sound(path)
            break
        except Exception:
            rock_sound = None
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

# Boss asset (optional)
boss_img = None
boss_path = os.path.join("Assets", "Boss Fight.GIF")
if os.path.exists(boss_path):
    try:
        boss_img = pygame.image.load(boss_path).convert_alpha()
        boss_img = pygame.transform.scale(boss_img, (320, 200))
    except Exception:
        boss_img = None

# 5. Player Setup
player_rect = player_img.get_rect()
player_rect.centerx = WIDTH // 2
player_rect.bottom = HEIGHT - 30
player_speed = 3  # Reduced from 5 to make the game slightly harder

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
asteroid_speed = 3 
spawn_timer = 0
spawn_delay = 180 

# Explosions list stores ongoing explosion effects (rect + timer)
explosions = []
# UFOs
ufos = []
ufo_speed = 4
ufo_spawn_timer = 0
ufo_spawn_delay = 600

# Boss state
boss = None
boss_speed = 3
boss_direction = 1
boss_health = 0
boss_max_health = 2500
boss_lasers = []
boss_fire_timer = 0
boss_fire_delay = 90  # frames between boss volleys
boss_laser_speed = 6

# Game state
game_over = False
player_dead = False
player_explosion_duration = 36  # frames the ship explosion plays before game over

# Fonts for UI
font = pygame.font.SysFont('Courier New', 72)
small_font = pygame.font.SysFont('Courier New', 36)
score_font = pygame.font.SysFont('Courier New', 32, bold=True)

# --- High Score Handling ---
# Load high score from file, if it exists
high_score_file = os.path.join("Assets", "high_score.txt")
if os.path.exists(high_score_file):
    with open(high_score_file, "r") as f:
        try:
            high_score = int(f.read().strip())
        except ValueError:
            high_score = 0  # If there's a problem, reset to 0
else:
    high_score = 0  # No high score file, start with 0

def reset_game():
    """Reset game state to start a new run."""
    global asteroids, ufos, lasers, explosions
    global spawn_timer, ufo_spawn_timer, bg_y1, bg_y2, game_over
    global player_dead, score
    score = 0

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




# --- Start Screen Implementation ---
def show_start_screen():
    waiting = True
    while waiting:
        screen.blit(background, (0, 0))
        title_text = font.render("SPACE SHOOTER", True, (255, 255, 80))
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
        screen.blit(title_text, title_rect)

        instr_text = small_font.render("Press SPACE to start", True, (255, 255, 255))
        instr_rect = instr_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
        screen.blit(instr_text, instr_rect)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

# Show start screen before game loop
show_start_screen()

score = 0  # Player score
high_score = 0  # Highest score in session

# 10. Game Loop
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
    spawn_timer += 3
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

    # Boss spawn check: when player reaches 5000 points, spawn the boss (if asset exists)
    # Only spawn boss once per game
    boss_spawned = False
    if 'boss_spawned' not in globals():
        boss_spawned = False
    if boss is None and not boss_spawned and score >= 5000 and boss_img is not None:
        boss = boss_img.get_rect()
        boss.centerx = WIDTH // 2
        boss.y = -boss.height
        boss_health = boss_max_health
        boss_spawned = True
        globals()['boss_spawned'] = True
        # clear minor enemies for boss intro
        asteroids = []
        ufos = []
        spawn_timer = 0
        ufo_spawn_timer = 0

    # If boss is active, ensure only boss is present: clear regular enemy spawning
    if boss is not None:
        # move boss into view until it reaches a set y position
        if boss.y < 60:
            boss.y += 2
        else:
            # Boss horizontal movement
            boss.x += boss_direction * boss_speed
            if boss.left <= 20:
                boss_direction = 1
            if boss.right >= WIDTH - 20:
                boss_direction = -1

            # Boss firing logic (one laser per side per volley)
            boss_fire_timer += 1
            if boss_fire_timer >= boss_fire_delay:
                boss_fire_timer = 0
                # alternate left/right cannon each volley
                if random.choice([True, False]):
                    left_laser = laser_img.get_rect()
                    left_laser.centerx = boss.left + 36
                    left_laser.top = boss.centery
                    boss_lasers.append(left_laser)
                else:
                    right_laser = laser_img.get_rect()
                    right_laser.centerx = boss.right - 36
                    right_laser.top = boss.centery
                    boss_lasers.append(right_laser)
                # play boss laser sound
                try:
                    shoot_sound.play()
                except Exception:
                    pass

        # while boss active, make sure regular enemies are cleared and not spawned
        asteroids = []
        ufos = []
        spawn_timer = 0
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
                # play rock explosion sound if available
                if rock_sound:
                    try:
                        rock_sound.play()
                    except Exception:
                        pass
                explosions.append({"rect": exp_rect, "timer": explosion_duration, "img": explosion_img})
                score += 50  # Add 50 points for asteroid
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
                score += 200  # Add 200 points for UFO
                destroyed_ufos.append(ufo)
                destroyed_lasers.append(laser)
                break

    if destroyed_ufos:
        ufos = [u for u in ufos if u not in destroyed_ufos]

    if destroyed_asteroids:
        asteroids = [a for a in asteroids if a not in destroyed_asteroids]
    if destroyed_lasers:
        lasers = [l for l in lasers if l not in destroyed_lasers]

    # Boss: player lasers hit boss
    if boss is not None:
        boss_destroyed = False
        for laser in lasers:
            if laser.colliderect(boss):
                boss_health -= 50  # player laser deals 50 damage
                destroyed_lasers.append(laser)
                # small explosion at hit
                exp_rect = explosion_img.get_rect()
                exp_rect.center = laser.center
                explosions.append({"rect": exp_rect, "timer": 8, "img": explosion_img})
                if boss_health <= 0:
                    boss_destroyed = True
                    break
        if boss_destroyed:
            # big explosion and reward
            exp_rect = ufo_explosion_img.get_rect()
            exp_rect.center = boss.center
            explosions.append({"rect": exp_rect, "timer": int(explosion_duration * 4), "img": ufo_explosion_img})
            score += 1000
            boss = None
            boss_lasers = []
            # After boss dies, normal gameplay resumes (asteroids/UFOs spawn again)

    # Move boss lasers
    new_boss_lasers = []
    for bl in boss_lasers:
        bl.y += boss_laser_speed
        # check collision with player
        if player_rect.colliderect(bl) and not player_dead:
            exp_rect = spaceship_explosion_img.get_rect()
            exp_rect.center = (player_rect.centerx, player_rect.centery - 12)
            if explosion_sound:
                try:
                    explosion_sound.play()
                except Exception:
                    pass
            explosions.append({"rect": exp_rect, "timer": player_explosion_duration, "img": spaceship_explosion_img})
            player_dead = True
        elif bl.top < HEIGHT:
            new_boss_lasers.append(bl)
    boss_lasers = new_boss_lasers

    # Check collisions between player and asteroids/UFOs -> game over
    # Use smaller hitboxes for asteroids and UFOs for fairer collision
    for asteroid in asteroids:
        asteroid_hitbox = asteroid.inflate(-20, -20)  # shrink by 20px each side
        if player_rect.colliderect(asteroid_hitbox) and not player_dead:
            # spawn ship explosion and mark player dead; nudge explosion upward so it centers visually
            exp_rect = spaceship_explosion_img.get_rect()
            exp_rect.center = (player_rect.centerx, player_rect.centery - 12)
            # play ship explosion sound if available
            if explosion_sound:
                try:
                    explosion_sound.play()
                except Exception:
                    pass
            explosions.append({"rect": exp_rect, "timer": player_explosion_duration, "img": spaceship_explosion_img})
            player_dead = True
            break
    for ufo in ufos:
        ufo_hitbox = ufo.inflate(-12, -12)  # shrink by 12px each side
        if player_rect.colliderect(ufo_hitbox) and not player_dead:
            exp_rect = spaceship_explosion_img.get_rect()
            exp_rect.center = (player_rect.centerx, player_rect.centery - 12)
            if explosion_sound:
                try:
                    explosion_sound.play()
                except Exception:
                    pass
            explosions.append({"rect": exp_rect, "timer": player_explosion_duration, "img": spaceship_explosion_img})
            player_dead = True
            break

    # Drawing player 
    screen.blit(background, (0, bg_y1)) 
    screen.blit(background, (0, bg_y2)) #Drawing scrolling background

    # If boss is active, display only boss and its lasers (and player)
    if boss is not None:
        # draw boss
        if boss_img:
            screen.blit(boss_img, boss)
        # draw boss lasers
        for bl in boss_lasers:
            screen.blit(laser_img, bl)
        # draw boss label and health bar (Alien King)
        label = small_font.render("Alien King", True, (255, 255, 255))
        label_rect = label.get_rect(center=(WIDTH//2, 12))
        screen.blit(label, label_rect)
        hb_w = 500
        hb_h = 22
        hb_x = (WIDTH - hb_w)//2
        hb_y = 30
        # outer border (green)
        pygame.draw.rect(screen, (0, 180, 0), (hb_x - 2, hb_y - 2, hb_w + 4, hb_h + 4), border_radius=4)
        # inner background (dark)
        pygame.draw.rect(screen, (30, 30, 30), (hb_x, hb_y, hb_w, hb_h))
        # red health fill
        health_ratio = max(0, boss_health) / boss_max_health
        pygame.draw.rect(screen, (200, 40, 40), (hb_x, hb_y, int(hb_w * health_ratio), hb_h))
        # draw player as well (player can still be hit)
        if not player_dead:
            screen.blit(player_img, player_rect)
    else:
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

        # (On-screen FPS counter removed)

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

    # Draw score at bottom right
    score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
    score_rect = score_text.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))
    screen.blit(score_text, score_rect)

    # If game over, display game over screen and wait for restart or quit
    if game_over:
        # Update high score if needed
        if score > high_score:
            high_score = score

        # darken background
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        go_text = font.render("GAME OVER", True, (255, 30, 30))
        go_rect = go_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 80))
        screen.blit(go_text, go_rect)

        score_text = small_font.render(f"Your Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(score_text, score_rect)

        high_score_text = small_font.render(f"High Score: {high_score}", True, (255, 255, 255))
        high_score_rect = high_score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
        screen.blit(high_score_text, high_score_rect)

        instr_text = small_font.render("Press R to restart or Q/Esc to quit", True, (255, 255, 255))
        instr_rect = instr_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 90))
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
    # Cap the frame rate to keep gameplay consistent across machines
    clock.tick(FPS)
pygame.quit()

# Save high score to file at the end of the game
with open(high_score_file, "w") as f:
    f.write(str(high_score))

