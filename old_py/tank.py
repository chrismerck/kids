import pygame
import sys
import math
import random
import numpy as np
from typing import List, Tuple

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1600  # Doubled from 800
SCREEN_HEIGHT = 1200  # Doubled from 600
FPS = 60
GRAVITY = 0.5  # Keeping same physics feel
GROUND_COLOR = (100, 80, 30)
SKY_COLOR = (135, 206, 235)
TANK_COLORS = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0)]
PROJECTILE_SPEED = 20  # Doubled from 10
EXPLOSION_RADIUS = 60  # Doubled from 30
TERRAIN_RESOLUTION = 1600  # Doubled from 800

class Terrain:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = self.generate_terrain()
        # Store surface heights for quick access
        self.surface_heights = self.calculate_surface_heights()
    
    def generate_terrain(self) -> np.ndarray:
        """Generate terrain using biased Brownian motion"""
        # Create empty 2D grid (False = air, True = ground)
        grid = np.zeros((self.width, self.height), dtype=bool)
        
        # Generate surface heights using the same algorithm as before
        heights = [int(self.height * 2/3)] * self.width
        current_height = heights[0]
        bias = 0
        
        for i in range(1, self.width):
            step = random.randint(-41, 40) + bias
            current_height += step
            current_height = max(self.height // 4, min(current_height, self.height - 50))
            
            if current_height < self.height * 0.5:
                bias = 1
            elif current_height > self.height * 0.7:
                bias = -1
            else:
                bias = 0
                
            heights[i] = current_height
            
        # Smooth the surface
        heights = self.smooth_terrain(heights, passes=10)
        
        # Fill the grid based on the surface heights
        for x in range(self.width):
            # Everything below the surface is ground
            for y in range(self.height - heights[x], self.height):
                grid[x, y] = True
        
        # Optionally, create some tunnels/caves
        self.create_caves(grid)
        
        return grid
    
    def create_caves(self, grid: np.ndarray, num_caves: int = 5):
        """Create random caves and tunnels in the terrain"""
        for _ in range(num_caves):
            # Random starting point below the surface
            x = random.randint(100, self.width - 100)  # Doubled from 50
            max_y = np.argmax(grid[x, :])  # Find first solid point
            y = random.randint(max_y + 40, self.height - 60)  # Doubled from 20, 30
            
            # Random size
            cave_width = random.randint(20, 60)  # Doubled from 10, 30
            cave_height = random.randint(10, 30)  # Doubled from 5, 15
            
            # Carve out the cave (elliptical shape)
            for dx in range(-cave_width, cave_width + 1):
                for dy in range(-cave_height, cave_height + 1):
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.width and 0 <= ny < self.height):
                        # Elliptical shape check
                        if (dx/cave_width)**2 + (dy/cave_height)**2 <= 1:
                            grid[nx, ny] = False
            
            # Possibly add a tunnel to the surface
            if random.random() < 0.5:  # 50% chance
                tunnel_x = x
                # Start at cave top
                tunnel_y = y - cave_height
                # Find surface
                while tunnel_y > 0 and not grid[tunnel_x, tunnel_y]:
                    tunnel_y -= 1
                # Carve tunnel
                for ty in range(tunnel_y, y - cave_height + 1):
                    for tx in range(tunnel_x - 4, tunnel_x + 5):  # Doubled width from 2 to 4
                        if 0 <= tx < self.width and 0 <= ty < self.height:
                            grid[tx, ty] = False
    
    def smooth_terrain(self, heights: List[int], passes: int = 3) -> List[int]:
        """Apply smoothing to the terrain"""
        smoothed = heights.copy()
        
        for _ in range(passes):
            new_heights = smoothed.copy()
            for i in range(1, len(smoothed) - 1):
                new_heights[i] = (smoothed[i-1] + smoothed[i] + smoothed[i+1]) // 3
            smoothed = new_heights
            
        return smoothed
    
    def calculate_surface_heights(self) -> List[int]:
        """Calculate heights of the surface for each x coordinate"""
        heights = []
        for x in range(self.width):
            # Find the first solid ground cell from top to bottom
            for y in range(self.height):
                if self.grid[x, y]:
                    heights.append(self.height - y)
                    break
            else:
                # No solid ground in this column
                heights.append(0)
        return heights
    
    def draw(self, screen):
        """Draw the terrain grid"""
        # Create a surface with the exact size of the grid
        terrain_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Use pygame.surfarray for faster drawing
        if hasattr(pygame, 'surfarray'):
            # Create an array representation of the terrain
            pixels = np.zeros((self.width, self.height, 4), dtype=np.uint8)
            # Set RGB and alpha values for solid cells
            r, g, b = GROUND_COLOR
            pixels[..., 0][self.grid] = r
            pixels[..., 1][self.grid] = g
            pixels[..., 2][self.grid] = b
            pixels[..., 3][self.grid] = 255  # Solid
            # Use surfarray.blit_array for efficient transfer
            pygame_surface_array = pygame.surfarray.pixels_alpha(terrain_surface)
            pygame_surface_array[...] = pixels[..., 3]
            del pygame_surface_array
            pygame_surface_array = pygame.surfarray.pixels3d(terrain_surface)
            pygame_surface_array[...] = pixels[..., :3]
            del pygame_surface_array
        else:
            # Fallback method
            for x in range(self.width):
                for y in range(self.height):
                    if self.grid[x, y]:
                        terrain_surface.set_at((x, y), GROUND_COLOR)
        
        # Blit the surface to the screen
        screen.blit(terrain_surface, (0, 0))
    
    def create_explosion(self, x: int, y: int, radius: int):
        """Modify terrain to create an explosion crater"""
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                # Check bounds
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    # Check if point is within the circular explosion radius
                    if dx*dx + dy*dy <= radius*radius:
                        self.grid[nx, ny] = False

        # Slide the terrain down
        self.slide_terrain()

        # Update surface heights after explosion
        self.surface_heights = self.calculate_surface_heights()

    def slide_terrain(self):
        """Slide the terrain down to fill in the crater"""
        for x in range(self.width):
            # count number of cells in column
            count = 0
            for y in range(self.height):
                if self.grid[x, y]:
                    count += 1
            # reconstruct the column
            for y in range(self.height):
                if y >= self.height - count:
                    self.grid[x, y] = True
                else:
                    self.grid[x, y] = False
    
    def get_height_at(self, x: int) -> int:
        """Get the surface height at position x"""
        if 0 <= x < self.width:
            return self.surface_heights[x]
        return 0
    
    def is_solid(self, x: int, y: int) -> bool:
        """Check if the point (x,y) is solid ground"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x, y]
        return False

class Tank:
    def __init__(self, x: int, terrain: Terrain, color: Tuple[int, int, int], player_num: int):
        self.terrain = terrain
        self.color = color
        self.player_num = player_num
        self.shields = 5
        self.width = 40  # Doubled from 20
        self.height = 20  # Doubled from 10
        self.barrel_length = 40  # Doubled from 20
        self.barrel_angle = 45  # Degrees (0 is right, 90 is up)
        self.set_position(x)
    
    def set_position(self, x: int):
        """Position the tank on the terrain at position x"""
        self.x = x
        # Place tank on top of terrain
        surface_height = self.terrain.get_height_at(x)
        self.y = SCREEN_HEIGHT - surface_height - self.height // 2
    
    def update_position(self):
        """Update the tank position if the ground beneath changed"""
        surface_height = self.terrain.get_height_at(self.x)
        target_y = SCREEN_HEIGHT - surface_height - self.height // 2
        
        # Move tank down if ground eroded beneath it
        if self.y < target_y:
            self.y = target_y
    
    def rotate_barrel(self, direction: int):
        """Rotate the barrel: -1 for CCW, 1 for CW"""
        self.barrel_angle += direction * 2
        self.barrel_angle = max(0, min(self.barrel_angle, 180))
    
    def get_barrel_end(self) -> Tuple[int, int]:
        """Get the coordinates of the end of the barrel"""
        angle_rad = math.radians(self.barrel_angle)
        barrel_x = self.x + math.cos(angle_rad) * self.barrel_length
        barrel_y = self.y - math.sin(angle_rad) * self.barrel_length
        return int(barrel_x), int(barrel_y)
    
    def draw(self, screen):
        """Draw the tank"""
        # Draw tank body
        pygame.draw.rect(screen, self.color, 
                         (self.x - self.width // 2, self.y - self.height // 2, 
                          self.width, self.height))
        
        # Draw barrel
        barrel_end = self.get_barrel_end()
        pygame.draw.line(screen, self.color, (self.x, self.y), barrel_end, 3)
        
        # Draw shield indicator on the tank
        font = pygame.font.SysFont(None, 20)
        shield_text = font.render(str(self.shields), True, (255, 255, 255))
        screen.blit(shield_text, (self.x - 5, self.y - 25))
    
    def fire(self) -> 'Projectile':
        """Fire a projectile from the tank barrel"""
        barrel_end = self.get_barrel_end()
        angle_rad = math.radians(self.barrel_angle)
        
        # Initial velocity components
        vx = math.cos(angle_rad) * PROJECTILE_SPEED
        vy = -math.sin(angle_rad) * PROJECTILE_SPEED
        
        return Projectile(barrel_end[0], barrel_end[1], vx, vy, self.color)
    
    def damage(self):
        """Reduce tank shields by 1"""
        self.shields -= 1
        return self.shields <= 0  # Return True if tank is destroyed

class Projectile:
    def __init__(self, x: float, y: float, vx: float, vy: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = 6  # Doubled from 3
        self.active = True
    
    def update(self, terrain: Terrain, tanks: List[Tank]) -> bool:
        """Update projectile position and check for collisions
        Returns True if the projectile has exploded"""
        if not self.active:
            return False
            
        # Apply gravity
        self.vy += GRAVITY
        
        # Store old position for collision detection
        old_x, old_y = self.x, self.y
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Check for wall/ceiling collisions
        if self.x < 0:
            self.x = 0
            self.vx = -self.vx * 0.8  # Bounce with energy loss
        elif self.x >= SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - 1
            self.vx = -self.vx * 0.8  # Bounce with energy loss
            
        if self.y < 0:
            self.y = 0
            self.vy = -self.vy * 0.8  # Bounce with energy loss
        
        # Check for terrain collision
        x_int, y_int = int(self.x), int(self.y)
        
        # Check if we've moved into solid terrain
        if terrain.is_solid(x_int, y_int):
            # Hit the terrain
            self.explode(terrain, tanks)
            return True
        
        # Check for line collision between old and new position
        # This ensures fast-moving projectiles don't skip over thin terrain
        if abs(self.vx) > 1 or abs(self.vy) > 1:
            steps = int(max(abs(self.vx), abs(self.vy))) * 2
            for i in range(1, steps + 1):
                t = i / steps
                check_x = int(old_x + (self.x - old_x) * t)
                check_y = int(old_y + (self.y - old_y) * t)
                if terrain.is_solid(check_x, check_y):
                    self.x, self.y = check_x, check_y
                    self.explode(terrain, tanks)
                    return True
                
        return False
    
    def draw(self, screen):
        """Draw the projectile"""
        if self.active:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
    
    def explode(self, terrain: Terrain, tanks: List[Tank]):
        """Handle explosion when projectile hits terrain"""
        self.active = False
        
        # Modify terrain
        terrain.create_explosion(int(self.x), int(self.y), EXPLOSION_RADIUS)
        
        # Check if any tanks are in the blast radius
        for tank in tanks:
            distance = math.sqrt((tank.x - self.x)**2 + (tank.y - self.y)**2)
            if distance < EXPLOSION_RADIUS:
                tank.damage()
                
        # Update tank positions after terrain changes
        for tank in tanks:
            tank.update_position()

class Game:
    def __init__(self, num_players: int = 2):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tank Game")
        self.clock = pygame.time.Clock()
        self.terrain = Terrain(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Create tanks
        self.num_players = max(2, min(num_players, 4))  # Between 2 and 4 players
        self.tanks = []
        
        positions = [SCREEN_WIDTH // (self.num_players + 1) * (i + 1) for i in range(self.num_players)]
        for i in range(self.num_players):
            self.tanks.append(Tank(positions[i], self.terrain, TANK_COLORS[i], i + 1))
        
        self.current_player = 0
        self.projectile = None
        self.game_over = False
        self.winner = None
        self.waiting_for_projectile = False
        
        # Track which keys are being held down
        self.keys_pressed = {pygame.K_LEFT: False, pygame.K_RIGHT: False}
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Only handle player inputs when no projectile is active
            if not self.waiting_for_projectile and not self.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        self.keys_pressed[event.key] = True
                    elif event.key == pygame.K_SPACE:
                        self.projectile = self.tanks[self.current_player].fire()
                        self.waiting_for_projectile = True
                        
                elif event.type == pygame.KEYUP:
                    if event.key in self.keys_pressed:
                        self.keys_pressed[event.key] = False
            
            # Allow restart when game is over
            if self.game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.__init__(self.num_players)
                
    def update(self):
        """Update game state"""
        # Handle continuous key presses for barrel rotation
        if not self.waiting_for_projectile and not self.game_over:
            if self.keys_pressed[pygame.K_LEFT]:
                self.tanks[self.current_player].rotate_barrel(1)  # CCW
            if self.keys_pressed[pygame.K_RIGHT]:
                self.tanks[self.current_player].rotate_barrel(-1)  # CW
        
        # Update projectile if active
        if self.waiting_for_projectile and self.projectile:
            if self.projectile.update(self.terrain, self.tanks):
                # Projectile exploded, move to next player
                self.projectile = None
                self.waiting_for_projectile = False
                self.next_player()
        
        # Check for game over
        active_players = 0
        last_active = -1
        for i, tank in enumerate(self.tanks):
            if tank.shields > 0:
                active_players += 1
                last_active = i
                
        if active_players <= 1 and self.num_players > 1:
            self.game_over = True
            self.winner = last_active + 1 if last_active >= 0 else None
                
    def next_player(self):
        """Move to the next player's turn"""
        self.current_player = (self.current_player + 1) % self.num_players
        
        # Skip destroyed tanks
        while self.tanks[self.current_player].shields <= 0:
            self.current_player = (self.current_player + 1) % self.num_players
    
    def draw(self):
        """Draw the game"""
        # Draw sky
        self.screen.fill(SKY_COLOR)
        
        # Draw terrain
        self.terrain.draw(self.screen)
        
        # Draw tanks
        for tank in self.tanks:
            tank.draw(self.screen)
            
        # Draw projectile if active
        if self.projectile:
            self.projectile.draw(self.screen)
            
        # Draw HUD
        self.draw_hud()
            
        pygame.display.flip()
        
    def draw_hud(self):
        """Draw the heads-up display"""
        font = pygame.font.SysFont(None, 64)  # Doubled from 32
        
        # Draw player shields
        for i, tank in enumerate(self.tanks):
            player_text = f"Player {i+1}: {tank.shields} shields"
            text_surface = font.render(player_text, True, tank.color)
            self.screen.blit(text_surface, (40 + i * 400, 40))  # Doubled from 20, 200
        
        # Highlight current player
        if not self.game_over:
            pygame.draw.rect(self.screen, (255, 255, 255), 
                            (30 + self.current_player * 400, 30, 380, 60), 4)  # Doubled all values
        
        # Game over message
        if self.game_over:
            if self.winner is not None:
                message = f"Player {self.winner} wins! Press R to restart"
            else:
                message = "Game over! Press R to restart"
                
            text_surface = font.render(message, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(text_surface, text_rect)
        
    def run(self):
        """Main game loop"""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game(num_players=4)  # Change the number of players as needed
    game.run()
