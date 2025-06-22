import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()

# Game constants
SCREEN_SIZE = 600
N_PLAYERS = 3  # Default number of players
PLAYER_RADIUS = 15
OBSTACLE_COUNT = 20
COIN_COUNT = 50
MAX_STAMINA = 500
COIN_RADIUS = 8
OBSTACLE_MIN_SIZE = 20
OBSTACLE_MAX_SIZE = 60

# Colors
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
PLAYER_COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow (for extra players)
    (255, 0, 255),  # Magenta (for extra players)
    (0, 255, 255)   # Cyan (for extra players)
]

# Create screen
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("N-Player Collection Game")
clock = pygame.time.Clock()

class Player:
    def __init__(self, idx):
        self.idx = idx
        self.color = PLAYER_COLORS[idx % len(PLAYER_COLORS)]
        self.reset_position()
        self.score = 0
        self.stamina = MAX_STAMINA
    
    def reset_position(self):
        # Place player at random position (ensuring not on obstacles)
        placed = False
        while not placed:
            self.x = random.randint(PLAYER_RADIUS, SCREEN_SIZE - PLAYER_RADIUS)
            self.y = random.randint(PLAYER_RADIUS, SCREEN_SIZE - PLAYER_RADIUS)
            placed = True  # Will be set to False if colliding with obstacles
    
    def draw(self, is_active):
        pygame.draw.circle(screen, self.color, (self.x, self.y), PLAYER_RADIUS)
        if is_active:
            pygame.draw.circle(screen, WHITE, (self.x, self.y), PLAYER_RADIUS + 3, 2)
    
    def move(self, dx, dy, obstacles):
        if self.stamina <= 0:
            return False
        
        # Calculate distance to move
        distance = math.sqrt(dx**2 + dy**2)
        if distance > self.stamina:
            # Scale down movement if it would exceed stamina
            dx = dx * self.stamina / distance
            dy = dy * self.stamina / distance
            distance = self.stamina
        
        # Check if move is valid (not hitting obstacles)
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Ensure player stays on screen
        if new_x < PLAYER_RADIUS:
            new_x = PLAYER_RADIUS
        elif new_x > SCREEN_SIZE - PLAYER_RADIUS:
            new_x = SCREEN_SIZE - PLAYER_RADIUS
        
        if new_y < PLAYER_RADIUS:
            new_y = PLAYER_RADIUS
        elif new_y > SCREEN_SIZE - PLAYER_RADIUS:
            new_y = SCREEN_SIZE - PLAYER_RADIUS
        
        # Check for obstacle collisions
        for obstacle in obstacles:
            if obstacle.collides_with_point(new_x, new_y, PLAYER_RADIUS):
                return False  # Can't move into an obstacle
        
        # Update position
        self.x = new_x
        self.y = new_y
        self.stamina -= distance
        return True

class Obstacle:
    def __init__(self):
        self.width = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
        self.height = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
        self.x = random.randint(0, SCREEN_SIZE - self.width)
        self.y = random.randint(0, SCREEN_SIZE - self.height)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)
    
    def collides_with_point(self, x, y, radius):
        # Check if a circle collides with this obstacle
        closest_x = max(self.x, min(x, self.x + self.width))
        closest_y = max(self.y, min(y, self.y + self.height))
        distance = math.sqrt((x - closest_x) ** 2 + (y - closest_y) ** 2)
        return distance < radius

class Coin:
    def __init__(self, color_idx):
        self.color_idx = color_idx
        self.color = PLAYER_COLORS[color_idx % len(PLAYER_COLORS)]
        self.x = random.randint(COIN_RADIUS, SCREEN_SIZE - COIN_RADIUS)
        self.y = random.randint(COIN_RADIUS, SCREEN_SIZE - COIN_RADIUS)
        self.collected = False
    
    def draw(self):
        if not self.collected:
            pygame.draw.circle(screen, self.color, (self.x, self.y), COIN_RADIUS)
    
    def check_collision(self, player):
        if not self.collected and player.idx == self.color_idx:
            distance = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
            if distance < PLAYER_RADIUS + COIN_RADIUS:
                self.collected = True
                player.score += 1
                return True
        return False

class Game:
    def __init__(self, n_players=N_PLAYERS):
        self.n_players = n_players
        self.active_player = 0
        self.players = [Player(i) for i in range(n_players)]
        
        # Create obstacles
        self.obstacles = []
        for _ in range(OBSTACLE_COUNT):
            self.obstacles.append(Obstacle())
        
        # Create coins (equal number for each player)
        self.coins = []
        for i in range(n_players):
            for _ in range(COIN_COUNT // n_players):
                self.coins.append(Coin(i))
        
        # Ensure no overlaps between game elements
        self.validate_positions()
        
        self.font = pygame.font.SysFont(None, 24)
        
    def validate_positions(self):
        # Make sure coins don't spawn on obstacles
        for coin in self.coins:
            placed = False
            while not placed:
                coin.x = random.randint(COIN_RADIUS, SCREEN_SIZE - COIN_RADIUS)
                coin.y = random.randint(COIN_RADIUS, SCREEN_SIZE - COIN_RADIUS)
                placed = True
                for obstacle in self.obstacles:
                    if obstacle.collides_with_point(coin.x, coin.y, COIN_RADIUS):
                        placed = False
                        break
        
        # Make sure players don't spawn on obstacles
        for player in self.players:
            placed = False
            while not placed:
                player.x = random.randint(PLAYER_RADIUS, SCREEN_SIZE - PLAYER_RADIUS)
                player.y = random.randint(PLAYER_RADIUS, SCREEN_SIZE - PLAYER_RADIUS)
                placed = True
                for obstacle in self.obstacles:
                    if obstacle.collides_with_point(player.x, player.y, PLAYER_RADIUS):
                        placed = False
                        break
    
    def next_player(self):
        self.active_player = (self.active_player + 1) % self.n_players
        self.players[self.active_player].stamina = MAX_STAMINA
    
    def draw(self):
        # Draw background
        screen.fill(BLACK)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw()
        
        # Draw coins
        for coin in self.coins:
            coin.draw()
        
        # Draw players
        for i, player in enumerate(self.players):
            player.draw(i == self.active_player)
        
        # Draw HUD
        self.draw_hud()
        
        pygame.display.flip()
    
    def draw_hud(self):
        # Draw player scores and stamina
        y_offset = 10
        for i, player in enumerate(self.players):
            # Player label
            text = f"Player {i+1}: {player.score} coins"
            text_surface = self.font.render(text, True, player.color)
            screen.blit(text_surface, (10, y_offset))
            
            # Stamina bar
            if i == self.active_player:
                # Draw stamina bar background
                pygame.draw.rect(screen, WHITE, (200, y_offset, 100, 20), 1)
                # Draw stamina bar fill
                pygame.draw.rect(screen, player.color, (200, y_offset, player.stamina, 20))
                # Show stamina text
                stamina_text = f"{int(player.stamina)}/{MAX_STAMINA}"
                stamina_surface = self.font.render(stamina_text, True, WHITE)
                screen.blit(stamina_surface, (310, y_offset))
            
            y_offset += 30
        
        # Show whose turn it is
        turn_text = f"Player {self.active_player + 1}'s Turn - Press SPACE for next player"
        turn_surface = self.font.render(turn_text, True, WHITE)
        screen.blit(turn_surface, (10, SCREEN_SIZE - 30))
    
    def update(self):
        # Check for coin collisions with active player
        for coin in self.coins:
            coin.check_collision(self.players[self.active_player])
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        player = self.players[self.active_player]
        
        # Movement keys
        dx, dy = 0, 0
        speed = 5  # Speed per frame
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += speed
        
        if dx != 0 or dy != 0:
            player.move(dx, dy, self.obstacles)

def main():
    game = Game(N_PLAYERS)
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.next_player()
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        game.handle_input()
        game.update()
        game.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
