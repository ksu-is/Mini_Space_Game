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


#Setting up momving background
background = pygame.image.load(os.path.join("assets", "background.png")) #Loading background image from assets folder
background = pygame.transform.scale(background, (WIDTH, HEIGHT)) #Scaling background image to fit game window

bg_y1 = 0 
bg_y2 = -HEIGHT #Allows two copies of background to move seamlessly


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

    pygame.display.update() #Updating display with new background positions
pygame.quit()

