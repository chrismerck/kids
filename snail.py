import pygame
import random
import time
import math
import os

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1600, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)  # Add grey color
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

# Set up colors for snails and die faces
COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE, CYAN]
COLOR_NAMES = ["RED", "GREEN", "BLUE", "YELLOW", "PURPLE", "CYAN"]

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snail Race")
clock = pygame.time.Clock()

# Game variables
snail_positions = [0] * 6  # All snails start at position 0
die_color = random.choice(COLORS)  # Initial random die color
die_spinning = False
spin_start_time = 0
spin_duration = 0
winner = None
die_just_stopped = False  # New flag to track when die has stopped

# Load snail image
try:
    snail_img = pygame.image.load('snail.jpg')
    # Scale the image to a reasonable size (adjust as needed)
    snail_img = pygame.transform.scale(snail_img, (30, 30))
except pygame.error:
    print("Warning: Could not load 'snail.jpg'. Using fallback graphics.")
    snail_img = None

def draw_track():
    # Draw the race track - increased width for a wider race track
    track_width = WIDTH * 0.8
    track_height = HEIGHT * 0.8
    track_x = 20
    track_y = 20
    
    # Draw track background - now black instead of white
    pygame.draw.rect(screen, BLACK, (track_x, track_y, track_width, track_height))
    pygame.draw.rect(screen, GREY, (track_x, track_y, track_width, track_height), 2)
    
    # Draw lane separators with GREY instead of BLACK
    lane_height = track_height / 6
    for i in range(1, 6):
        y = track_y + i * lane_height
        pygame.draw.line(screen, GREY, (track_x, y), (track_x + track_width, y))
    
    # Draw position markers with GREY instead of BLACK
    position_width = track_width / 10
    for i in range(1, 10):
        x = track_x + i * position_width
        pygame.draw.line(screen, GREY, (x, track_y), (x, track_y + track_height))
        
        # Label finish line - now WHITE text instead of BLACK
        if i == 9:
            font = pygame.font.SysFont('Arial', 20)
            finish_text = font.render("FINISH", True, WHITE)
            screen.blit(finish_text, (x - 30, track_y - 25))
    
    # Draw snails
    for i in range(6):
        snail_color = COLORS[i]
        y = track_y + i * lane_height + lane_height // 2
        x = track_x + snail_positions[i] * position_width + position_width // 2
        
        # Make the colored circle slightly larger for better visibility on wider track
        pygame.draw.circle(screen, snail_color, (int(x), int(y)), 25)  # Increased from 20 to 25
        
        if snail_img:
            # Use a wider snail image that's twice as wide as tall
            # We scale the image to be wider (60x30 instead of 30x30)
            scaled_img = pygame.transform.scale(snail_img, (60, 30))
            img_rect = scaled_img.get_rect(center=(int(x), int(y)))
            screen.blit(scaled_img, img_rect)
        else:
            # Fallback to original drawing if image not available
            pygame.draw.circle(screen, BLACK, (int(x), int(y)), 15, 2)
            pygame.draw.circle(screen, (snail_color[0]//2, snail_color[1]//2, snail_color[2]//2), 
                              (int(x) + 5, int(y) - 5), 5)

def draw_die():
    global die_spinning, die_just_stopped
    # Reposition the die to fit in the wider window
    die_width = WIDTH * 0.1  # Reduced from 0.2 to 0.1 for better proportions
    die_height = die_width
    die_x = WIDTH - die_width - 40  # Increased margin from 20 to 40
    die_y = (HEIGHT - die_height) // 2
    
    # Draw die background - now BLACK with GREY outline
    pygame.draw.rect(screen, BLACK, (die_x, die_y, die_width, die_height))
    pygame.draw.rect(screen, GREY, (die_x, die_y, die_width, die_height), 2)
    
    if die_spinning:
        # Draw spinning animation
        current_time = time.time()
        elapsed = current_time - spin_start_time
        
        if elapsed >= spin_duration:
            die_spinning = False
            die_just_stopped = True  # Set flag when die stops spinning
            return
        
        # Make the die appear to spin by changing colors rapidly
        spin_color_index = int((elapsed * 20) % 6)
        spin_color = COLORS[spin_color_index]
        
        # Draw a spinning cube effect
        for i in range(4):
            angle = elapsed * 5 + i * math.pi / 2
            offset_x = math.cos(angle) * 20
            offset_y = math.sin(angle) * 20
            pygame.draw.rect(screen, spin_color, 
                            (die_x + die_width/2 - 30 + offset_x, 
                             die_y + die_height/2 - 30 + offset_y, 
                             60, 60))
    else:
        # Draw the die with the current color
        pygame.draw.rect(screen, die_color, (die_x + 20, die_y + 20, die_width - 40, die_height - 40))
        
        # Draw die dots to make it look more like a die - now WHITE dots
        dot_color = WHITE  # Changed from BLACK to WHITE
        center_x = die_x + die_width // 2
        center_y = die_y + die_height // 2
        radius = 5
        
        # Pattern depends on the color (mimicking a real die layout)
        color_index = COLORS.index(die_color)
        if color_index in [0, 5]:  # 1 or 6 dots
            pygame.draw.circle(screen, dot_color, (center_x, center_y), radius)
            if color_index == 5:  # 6 dots
                pygame.draw.circle(screen, dot_color, (center_x - 20, center_y - 20), radius)
                pygame.draw.circle(screen, dot_color, (center_x + 20, center_y - 20), radius)
                pygame.draw.circle(screen, dot_color, (center_x - 20, center_y + 20), radius)
                pygame.draw.circle(screen, dot_color, (center_x + 20, center_y + 20), radius)
                pygame.draw.circle(screen, dot_color, (center_x - 20, center_y), radius)
                pygame.draw.circle(screen, dot_color, (center_x + 20, center_y), radius)
        elif color_index in [1, 4]:  # 2 or 5 dots
            pygame.draw.circle(screen, dot_color, (center_x - 20, center_y - 20), radius)
            pygame.draw.circle(screen, dot_color, (center_x + 20, center_y + 20), radius)
            if color_index == 4:  # 5 dots
                pygame.draw.circle(screen, dot_color, (center_x, center_y), radius)
                pygame.draw.circle(screen, dot_color, (center_x - 20, center_y + 20), radius)
                pygame.draw.circle(screen, dot_color, (center_x + 20, center_y - 20), radius)
        else:  # 3 or 4 dots
            pygame.draw.circle(screen, dot_color, (center_x - 20, center_y - 20), radius)
            pygame.draw.circle(screen, dot_color, (center_x + 20, center_y + 20), radius)
            pygame.draw.circle(screen, dot_color, (center_x - 20, center_y + 20), radius)
            if color_index == 3:  # 4 dots
                pygame.draw.circle(screen, dot_color, (center_x + 20, center_y - 20), radius)
    
    # Display current die color as text - now WHITE text
    font = pygame.font.SysFont('Arial', 16)
    color_index = COLORS.index(die_color)
    color_text = font.render(f"Die Color: {COLOR_NAMES[color_index]}", True, WHITE)
    screen.blit(color_text, (die_x, die_y - 30))

def spin_die():
    global die_spinning, spin_start_time, spin_duration, die_color
    
    if not die_spinning:
        die_spinning = True
        spin_start_time = time.time()
        spin_duration = random.uniform(1.0, 2.0)  # Spin for 1-2 seconds
        die_color = random.choice(COLORS)  # Pre-select the result

def move_snail(color):
    color_index = COLORS.index(color)
    if snail_positions[color_index] < 9:
        snail_positions[color_index] += 1
    
    # Check for winner
    if snail_positions[color_index] >= 9:
        global winner
        winner = color_index

def reset_game():
    global snail_positions, winner
    snail_positions = [0] * 6
    winner = None

def main():
    global winner, die_just_stopped
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not die_spinning:
                    if winner is not None:
                        reset_game()
                    else:
                        spin_die()
                    
        # Only move snail when die has just stopped spinning
        if die_just_stopped and winner is None:
            move_snail(die_color)
            die_just_stopped = False  # Reset the flag after moving
        
        # Clear screen
        if winner is not None:
            # If there's a winner, fill screen with winning color
            screen.fill(COLORS[winner])
            
            # Display winner message - keep text BLACK for contrast on colored background
            font = pygame.font.SysFont('Arial', 40)
            win_text = font.render(f"{COLOR_NAMES[winner]} SNAIL WINS!", True, BLACK)
            text_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(win_text, text_rect)
            
            restart_text = font.render("Press SPACE to restart", True, BLACK)
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            screen.blit(restart_text, restart_rect)
            
            # Wait for space to restart
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                reset_game()
        else:
            # Normal gameplay - now BLACK background instead of light grey
            screen.fill(BLACK)
            draw_track()
            draw_die()
            
            # Instructions - now WHITE text
            font = pygame.font.SysFont('Arial', 16)
            instructions = font.render("Press SPACE to roll the die", True, WHITE)
            screen.blit(instructions, (WIDTH // 2 - 100, HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
    pygame.quit()
