#Importing necessary modules
import pygame # Importing pygame for game development
import random # Importing random module for enemy positions and movements
import os # Importing os module to load files from assets folder

pygame.init() # This line starts the pygame module

# Setting up the game window dimensions and title
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame. display.set_caption("Space Shooter")


# Setting up the background
background = pygame.image.load(os.path.join("Assets", "Background.png")) # Loading background image from Assets folder
background = pygame.transform.scale(background, (WIDTH, HEIGHT)) # Scaling background image to fit game window

bg_y1 = 0 
bg_y2 = -HEIGHT #Allows two copies of background to move seamlessly

# Adding player spaceship
# Load player image and create rectangle
player_img = pygame.image.load(os.path.join("Assets", "Player.png")).convert_alpha()
# Optionally scale player
player_img = pygame.transform.scale(player_img, (64, 64))
player_rect = player_img.get_rect()
# Start player near the bottom center
player_rect.centerx = WIDTH // 2
player_rect.bottom = HEIGHT - 30
player_speed = 5


# Adding the game loop
running = True #This runs the game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False # Allows you to click "x" to close the game window


    #Drawing and scrolling background in game loop
    screen.blit(background, (0, bg_y1)) 
    screen.blit(background, (0, bg_y2)) #Drawing scrolling background


    bg_y1 += 2 
    bg_y2 += 2 #Moving background downwards


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

    # Drawing player 
    screen.blit(player_img, player_rect)

    pygame.display.update() #Updating display with new background positions
pygame.quit() 

