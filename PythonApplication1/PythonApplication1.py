import pygame as pg
from random import randrange
from moviepy.editor import VideoFileClip

# Constants
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
TILE_SIZE = 100 #tile size of game set to 100 
INITIAL_SPEED = 8 #speed of snake 
SPEED_INCREMENT_INTERVAL = 15 #snake spped increments every 15
RELOAD_INTERVAL = 5000  # 5 seconds in milliseconds

def get_random_position():
    return [randrange(TILE_SIZE // 2, WINDOW_WIDTH - TILE_SIZE // 2, TILE_SIZE), #spawns random x position
            randrange(TILE_SIZE // 2, WINDOW_HEIGHT - TILE_SIZE // 2 - 100, TILE_SIZE)]  # spawns random y Adjust for HUD height

# Function to play the intro video
def play_intro_video(video_path):
    clip = VideoFileClip(video_path)
    clip.preview(fullscreen=True)  # Play the video in fullscreen
    clip.close()  # Close the clip when done

# Initialize Pygame
pg.init()
pg.mixer.init() #audio for pygame

# Play the intro video
play_intro_video('doomvideoo.mp4')  # Adjust the path to your video file

# Set up the screen
screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) #creates the game window
clock = pg.time.Clock() #controls the framerate

# Load images
doomguy_img = pg.image.load('doomslay.png')
doomguy_img = pg.transform.scale(doomguy_img, (TILE_SIZE, TILE_SIZE))
monster_img = pg.image.load('monster.png')
monster_img = pg.transform.scale(monster_img, (TILE_SIZE, TILE_SIZE))
background_img = pg.image.load('doomwall.jpg')
background_img = pg.transform.scale(background_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
dead_skull_img = pg.image.load('dead_skull.png')
dead_skull_img = pg.transform.scale(dead_skull_img, (TILE_SIZE, TILE_SIZE))

# Load the HUD image
hud_img = pg.image.load('doomhud.png')
hud_img = pg.transform.scale(hud_img, (WINDOW_WIDTH, 100))

# Load sounds
eat_sound = pg.mixer.Sound('shotgun.wav')  # Load the eat sound effect
reload_sound = pg.mixer.Sound('reload.mp3')  # Load the reload sound effect
blood_sound = pg.mixer.Sound('blood.mp3')  # Load the blood sound effect

# Initialize game variables
running = True
game_started = False

# Show a message to press Enter to start
font = pg.font.Font(None, 74) 
text = font.render('Press ENTER to Start', True, (255, 255, 255)) #starts the game when video is done 
text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

while running:
    for event in pg.event.get(): #process events in a queue
        if event.type == pg.QUIT: #check if window is closed
            running = False #false funning it will exit loop 
        if event.type == pg.KEYDOWN: #check if enter is pressed 
            if event.key == pg.K_RETURN:  # Press Enter to start the game
                game_started = True #set game to start
                pg.mixer.music.load('rip_and_tear.mp3') #loads the music 
                pg.mixer.music.play(-1)  # Start playing the music

    if not game_started:
        screen.fill((0, 0, 0))  # Fill screen with black
        screen.blit(text, text_rect)  # Draw the start message
    else:
        break  # Exit the loop to start the game

# Initial snake setup
initial_x = (WINDOW_WIDTH // 2) // TILE_SIZE * TILE_SIZE  #x position for snake 
initial_y = (WINDOW_HEIGHT // 2) // TILE_SIZE * TILE_SIZE #y position for snake 
snake = pg.Rect(initial_x, initial_y, TILE_SIZE, TILE_SIZE) #rectangles created for snakes head
segments = [snake.copy()] #creates a list to hold snake segments 
length = 1 #starting lenght of the snake 
direction = pg.Vector2(1, 0) #begning direction of the snake 

# Food setup
food = pg.Rect(get_random_position(), (TILE_SIZE, TILE_SIZE))

# Speed and timer setup
speed = INITIAL_SPEED #current speed of snake 
last_speed_up_time = pg.time.get_ticks() #current time for speed managment 
last_reload_time = pg.time.get_ticks() #current time for reload sound 

# Track how many food items have been eaten
food_eaten_count = 0

while True: #maingame loop
    for event in pg.event.get(): #process the events 
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and direction.y != 1: #move up if not moving down 
                direction = pg.Vector2(0, -1)
            elif event.key == pg.K_DOWN and direction.y != -1: #move down if not moving up 
                direction = pg.Vector2(0, 1)
            elif event.key == pg.K_LEFT and direction.x != 1: #move left if not moving right 
                direction = pg.Vector2(-1, 0)
            elif event.key == pg.K_RIGHT and direction.x != -1:#move right if not moving left 
                direction = pg.Vector2(1, 0)

    # Move the snake
    new_head = segments[0].copy() #copy of currents head position
    new_head.x += direction.x * TILE_SIZE #updates location
    new_head.y += direction.y * TILE_SIZE #updates location
    segments.insert(0, new_head) #makes a new head

    if new_head.colliderect(food): #checks to see if head eats food 
        eat_sound.play()  # Play the eating sound effect
        length += 1 #increments the segment if it does
        food.topleft = get_random_position() #respawns food 

        # Track food eaten
        food_eaten_count += 1
        if food_eaten_count >= 10: #if 10 food eaten 
            blood_sound.play()  # Play the blood sound effect
            food_eaten_count = 0  # Reset the count
    else:
        segments.pop()

    if (new_head.x < 0 or new_head.x >= WINDOW_WIDTH or #check if head out of bounds left or right 
        new_head.y < 0 or new_head.y >= WINDOW_HEIGHT - 100 or  # check if out of bounds top or bottom
        segments[0] in segments[1:]): #check if it collides with its own body 
        pg.quit() #quits the game if it does
        exit()

    current_time = pg.time.get_ticks()
    
    # Speed up logic
    if (current_time - last_speed_up_time) >= SPEED_INCREMENT_INTERVAL * 1000: #check if speed up interval has passed
        speed += 1 #speed up snake
        last_speed_up_time = current_time #update last speed to current time 
    
    # Reload sound logic
    if (current_time - last_reload_time) >= RELOAD_INTERVAL:
        reload_sound.stop()  # Stop the sound if it's playing
        reload_sound.play()  # Play the reload sound
        last_reload_time = current_time  # Update the last reload time

    # Drawing
    screen.blit(background_img, (0, 0)) #displays background at center 
    for index, segment in enumerate(segments): #iterates through the segments of the snake 
        if index == 0: #checks it 
            screen.blit(doomguy_img, segment.topleft) #draws the head as doomslayer
        else:
            screen.blit(dead_skull_img, segment.topleft) #draws the body as dead skulls

    screen.blit(monster_img, food.topleft) #displays the food (monster)

    # Draw the HUD at the bottom of the screen
    screen.blit(hud_img, (0, WINDOW_HEIGHT - 100))  # Position the HUD at the bottom

    pg.display.flip()  # Update the display
    clock.tick(speed)  # Control the frame rate