import pygame
import random
import sys
import argparse
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FONT_SIZE = 36
SMALL_FONT_SIZE = 24
CAT_SIZE = 70
DOG_SIZE = 80
BOSS_SIZE = 150  # Bigger size for the boss
BUTTON_SIZE = 50
GAP = 20
Y_OFFSET = 80  # Vertical offset to position elements lower on screen
CENTER_X = SCREEN_WIDTH // 2 - CAT_SIZE // 2  # Center X position for cats when clicked

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)
LIGHT_RED = (255, 182, 193)

# Game class
class NineLives:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("9 Lives - Math Game")
        
        # Load fonts
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.small_font = pygame.font.SysFont(None, SMALL_FONT_SIZE)
        
        # Load images
        try:
            cat_image = pygame.image.load("cat.jpg")
            self.cat_img = pygame.transform.scale(cat_image, (CAT_SIZE, CAT_SIZE))
            
            dog_image = pygame.image.load("dog.jpg")
            self.dog_img = pygame.transform.scale(dog_image, (DOG_SIZE, DOG_SIZE))
        except pygame.error:
            # Fallback to colored rectangles if images can't be loaded
            self.cat_img = pygame.Surface((CAT_SIZE, CAT_SIZE))
            self.cat_img.fill(LIGHT_BLUE)
            self.dog_img = pygame.Surface((DOG_SIZE, DOG_SIZE))
            self.dog_img.fill(LIGHT_RED)
        
        # Initialize game variables
        self.total_rounds = 9
        self.current_round = 1
        self.reset_round()
        
    def reset_round(self):
        # Initialize cats (3x3 grid)
        self.cats = []
        self.cat_numbers = []
        for i in range(9):
            self.cat_numbers.append(random.randint(1, 9))
            row, col = i // 3, i % 3
            x = col * (CAT_SIZE + GAP) + GAP  # No X_OFFSET
            y = row * (CAT_SIZE + GAP) + GAP + Y_OFFSET
            cat_rect = pygame.Rect(x, y, CAT_SIZE, CAT_SIZE)
            self.cats.append({
                'rect': cat_rect,
                'original_pos': (x, y),  # Store original position
                'target_pos': (x, y),    # Target position for movement
                'number': self.cat_numbers[i],
                'alive': True,
                'selected': False,
                'advancing': False,      # Flag to track if cat is moving
                'used': False            # Flag to track if cat has been used in current expression
            })
        
        # Check if it's the boss round (round 9)
        self.is_boss_round = (self.current_round == 9)
        
        if self.is_boss_round:
            # Initialize the boss
            self.boss = {
                'rect': pygame.Rect(SCREEN_WIDTH - BOSS_SIZE - GAP, Y_OFFSET, BOSS_SIZE, BOSS_SIZE),
                'max_hp': random.randint(100, 1000),
                'current_hp': 0,  # Will be set to max_hp after initialization
                'alive': True
            }
            self.boss['current_hp'] = self.boss['max_hp']
            
            # No regular dogs in boss round
            self.dogs = []
        else:
            # Initialize dogs (2 in column) for regular rounds
            self.dogs = []
            self.dog_numbers = []
            for i in range(2):
                self.dog_numbers.append(random.randint(1, 100))
                x = SCREEN_WIDTH - DOG_SIZE - GAP
                y = i * (DOG_SIZE + GAP) + GAP + Y_OFFSET
                dog_rect = pygame.Rect(x, y, DOG_SIZE, DOG_SIZE)
                self.dogs.append({
                    'rect': dog_rect,
                    'number': self.dog_numbers[i],
                    'alive': True
                })
            
            # No boss in regular rounds
            self.boss = None
        
        # Initialize operation buttons
        self.buttons = []
        operations = ['+', '-', '×', '(', ')', '⚔️']
        for i, op in enumerate(operations):
            x = (SCREEN_WIDTH // 7) * (i + 1) - BUTTON_SIZE // 2
            y = SCREEN_HEIGHT - BUTTON_SIZE - GAP
            button_rect = pygame.Rect(x, y, BUTTON_SIZE, BUTTON_SIZE)
            self.buttons.append({
                'rect': button_rect,
                'operation': op,
                'selected': False
            })
        
        # Game state
        self.current_expression = []
        self.current_value = 0
        self.expression_text = ""
        self.game_over = False
        self.win = False
        self.open_parens = 0  # Track the number of open parentheses
        self.selected_cats_count = 0  # Keep track of how many cats are selected for column positioning
    
    def calculate_value(self):
        if not self.current_expression:
            return 0
        
        try:
            # Convert the expression to a string that can be evaluated
            expr_str = ""
            for item in self.current_expression:
                if item == '×':
                    expr_str += '*'  # Replace × with * for evaluation
                else:
                    expr_str += str(item)
            
            # Use eval to calculate the result (safe here since we control all input)
            result = eval(expr_str)
            return result
        except:
            # If there's an error in evaluation, return 0
            return 0
    
    def is_valid_expression_addition(self, item):
        """Check if adding the item to the expression would maintain valid grammar"""
        # Empty expressions can accept numbers or opening parenthesis
        if not self.current_expression:
            return isinstance(item, int) or item == '('
        
        last_item = self.current_expression[-1]
        
        # After a number, can add operator or closing parenthesis
        if isinstance(last_item, int):
            if item in ['+', '-', '×']:
                return True
            elif item == ')' and self.open_parens > 0:
                return True
            return False
        
        # After an operator, can add number or opening parenthesis
        if last_item in ['+', '-', '×']:
            return isinstance(item, int) or item == '('
        
        # After opening parenthesis, can add number or another opening parenthesis
        if last_item == '(':
            return isinstance(item, int) or item == '('
        
        # After closing parenthesis, can add operator or another closing parenthesis
        if last_item == ')':
            if item in ['+', '-', '×']:
                return True
            elif item == ')' and self.open_parens > 0:
                return True
            return False
        
        return False
    
    def update_expression_text(self):
        self.expression_text = " ".join(str(item) for item in self.current_expression)
        self.current_value = self.calculate_value()
    
    def update_cats(self):
        """Update cat positions for animation"""
        movement_speed = 5  # Pixels per frame
        for cat in self.cats:
            if cat['alive']:
                current_x, current_y = cat['rect'].x, cat['rect'].y
                target_x, target_y = cat['target_pos']
                
                # Calculate direction and distance
                dx = target_x - current_x
                dy = target_y - current_y
                distance = (dx**2 + dy**2)**0.5
                
                if distance > 0:
                    # If not at target position, move toward it
                    if distance <= movement_speed:
                        # Close enough, snap to target
                        cat['rect'].x = target_x
                        cat['rect'].y = target_y
                    else:
                        # Move in the direction of the target
                        move_x = dx * movement_speed / distance
                        move_y = dy * movement_speed / distance
                        cat['rect'].x += move_x
                        cat['rect'].y += move_y
    
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            # Check if a cat was clicked
            for i, cat in enumerate(self.cats):
                if cat['rect'].collidepoint(event.pos) and cat['alive'] and not cat['used']:
                    # Check if adding a number is valid in the current expression
                    if self.is_valid_expression_addition(cat['number']):
                        cat['selected'] = True
                        cat['used'] = True  # Mark the cat as used
                        
                        # Move the cat to the middle of the screen in a column
                        # Calculate Y position based on how many cats are already selected
                        column_y = (SCREEN_HEIGHT // 2) - (CAT_SIZE // 2) - (self.selected_cats_count * (CAT_SIZE + 10))
                        
                        # Set target position in the center column
                        cat['target_pos'] = (CENTER_X, column_y)
                        
                        # Increment selected cats counter
                        self.selected_cats_count += 1
                        
                        self.current_expression.append(cat['number'])
                        self.update_expression_text()
            
            # Check if an operation button was clicked
            for button in self.buttons:
                if button['rect'].collidepoint(event.pos):
                    operation = button['operation']
                    
                    if operation == '⚔️':
                        # Check if expression is valid before battle
                        if self.open_parens == 0 and len(self.current_expression) > 0:
                            self.battle()
                    elif operation == '(':
                        # Check if adding an opening parenthesis is valid
                        if self.is_valid_expression_addition('('):
                            self.current_expression.append('(')
                            self.open_parens += 1
                            self.update_expression_text()
                    elif operation == ')':
                        # Check if adding a closing parenthesis is valid
                        if self.is_valid_expression_addition(')'):
                            self.current_expression.append(')')
                            self.open_parens -= 1
                            self.update_expression_text()
                    elif self.is_valid_expression_addition(operation):
                        # Add operation if valid
                        self.current_expression.append(operation)
                        self.update_expression_text()
    
    def battle(self):
        if not self.current_expression or self.open_parens > 0:
            return
        
        if self.is_boss_round and self.boss and self.boss['alive']:
            # In boss round, damage is based on the calculated value
            damage = self.current_value
            self.boss['current_hp'] = max(0, self.boss['current_hp'] - damage)
            
            # Check if boss is defeated
            if self.boss['current_hp'] <= 0:
                self.boss['alive'] = False
        else:
            # Regular round logic
            # Check if the current value matches any dog's number
            dog_hit = False
            for dog in self.dogs:
                if dog['alive'] and dog['number'] == self.current_value:
                    dog['alive'] = False
                    dog_hit = True
                    break
            
            # If no dog was hit, the selected cats die
            if not dog_hit:
                for cat in self.cats:
                    if cat['selected']:
                        cat['alive'] = False
                        cat['selected'] = False
        
        # Reset the expression and parenthesis counter
        self.current_expression = []
        self.expression_text = ""
        self.open_parens = 0
        
        # Reset cat selections but keep used cats in the middle
        for cat in self.cats:
            cat['selected'] = False
            # Only reset position for cats that are no longer used (already dead)
            if not cat['alive']:
                cat['used'] = False  # Reset used status for dead cats
                cat['target_pos'] = cat['original_pos']  # Return dead cats to original positions
            # Keep used cats in the middle
        
        # Reset selected cats counter
        self.selected_cats_count = 0
        
        # Check win/lose conditions
        self.check_game_state()
    
    def check_game_state(self):
        if self.is_boss_round and self.boss:
            # Boss round: win if boss is defeated
            if not self.boss['alive']:
                self.win = True
                self.game_over = True
                self.current_round += 1  # This should now be 10, beyond the total rounds
        else:
            # Regular round: win if all dogs are dead
            dogs_alive = sum(1 for dog in self.dogs if dog['alive'])
            if dogs_alive == 0:
                self.win = True
                self.game_over = True
                self.current_round += 1
                if self.current_round <= self.total_rounds:
                    self.reset_round()
                    self.game_over = False
                    self.win = False
        
        # Check if all cats are dead (lose)
        cats_alive = sum(1 for cat in self.cats if cat['alive'])
        if cats_alive == 0:
            self.win = False
            self.game_over = True
    
    def draw(self):
        # Fill background
        self.screen.fill(WHITE)
        
        # Draw cats
        for i, cat in enumerate(self.cats):
            if cat['alive']:
                if cat['selected']:
                    # Add a green outline for selected cats
                    outline = pygame.Rect(cat['rect'].x - 2, cat['rect'].y - 2, 
                                         cat['rect'].width + 4, cat['rect'].height + 4)
                    pygame.draw.rect(self.screen, LIGHT_GREEN, outline)
                
                # Draw cat image
                self.screen.blit(self.cat_img, cat['rect'])
                
                # Draw number above cat
                num_text = self.font.render(str(cat['number']), True, BLACK)
                num_rect = num_text.get_rect(centerx=cat['rect'].centerx, bottom=cat['rect'].top - 5)
                self.screen.blit(num_text, num_rect)
        
        if self.is_boss_round and self.boss:
            # Draw boss
            if self.boss['alive']:
                # Create a bigger surface for the boss if we need one
                try:
                    # Use dog image for boss but larger
                    boss_img = pygame.transform.scale(self.dog_img, (BOSS_SIZE, BOSS_SIZE))
                    self.screen.blit(boss_img, self.boss['rect'])
                except:
                    # Fallback to colored rectangle
                    pygame.draw.rect(self.screen, LIGHT_RED, self.boss['rect'])
                
                # Draw boss HP bar
                hp_width = 150
                hp_height = 15
                hp_x = self.boss['rect'].centerx - hp_width // 2
                hp_y = self.boss['rect'].top - 40
                
                # Background bar (total HP)
                pygame.draw.rect(self.screen, GRAY, (hp_x, hp_y, hp_width, hp_height))
                
                # Current HP bar
                hp_percent = self.boss['current_hp'] / self.boss['max_hp']
                current_hp_width = int(hp_width * hp_percent)
                pygame.draw.rect(self.screen, LIGHT_RED, (hp_x, hp_y, current_hp_width, hp_height))
                
                # HP text
                hp_text = self.small_font.render(f"HP: {self.boss['current_hp']}/{self.boss['max_hp']}", True, BLACK)
                hp_text_rect = hp_text.get_rect(centerx=self.boss['rect'].centerx, bottom=hp_y - 5)
                self.screen.blit(hp_text, hp_text_rect)
                
                # Boss title
                boss_text = self.font.render("FINAL BOSS", True, BLACK)
                boss_text_rect = boss_text.get_rect(centerx=self.boss['rect'].centerx, bottom=self.boss['rect'].top - 50)
                self.screen.blit(boss_text, boss_text_rect)
        else:
            # Draw dogs (regular rounds)
            for dog in self.dogs:
                if dog['alive']:
                    # Draw dog image
                    self.screen.blit(self.dog_img, dog['rect'])
                    
                    # Draw number above dog
                    num_text = self.font.render(str(dog['number']), True, BLACK)
                    num_rect = num_text.get_rect(centerx=dog['rect'].centerx, bottom=dog['rect'].top - 5)
                    self.screen.blit(num_text, num_rect)
        
        # Draw operation buttons
        for button in self.buttons:
            pygame.draw.rect(self.screen, GRAY, button['rect'])
            btn_text = self.font.render(button['operation'], True, BLACK)
            btn_rect = btn_text.get_rect(center=button['rect'].center)
            self.screen.blit(btn_text, btn_rect)
        
        # Draw current expression and value
        if self.expression_text:
            expr_text = self.small_font.render(self.expression_text, True, BLACK)
            value_text = self.font.render(f"= {self.current_value}", True, BLACK)
            
            # Position the expression text with better wrapping if it's long
            if len(self.expression_text) > 30:
                lines = []
                current_line = ""
                for part in self.expression_text.split():
                    if len(current_line + " " + part) <= 30:
                        current_line += " " + part if current_line else part
                    else:
                        lines.append(current_line)
                        current_line = part
                if current_line:
                    lines.append(current_line)
                
                for i, line in enumerate(lines):
                    line_text = self.small_font.render(line, True, BLACK)
                    line_rect = line_text.get_rect(center=(SCREEN_WIDTH // 2, 
                                                          SCREEN_HEIGHT // 2 - 50 + i * 25))
                    self.screen.blit(line_text, line_rect)
            else:
                expr_rect = expr_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
                self.screen.blit(expr_text, expr_rect)
            
            value_rect = value_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(value_text, value_rect)
            
            # Show warning if parentheses don't match
            if self.open_parens > 0:
                warning_text = self.small_font.render("Missing closing parentheses", True, (255, 0, 0))
                warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
                self.screen.blit(warning_text, warning_rect)
        
        # Draw round info with special indicator for boss round
        if self.is_boss_round:
            round_text = self.small_font.render(f"BOSS ROUND! ({self.current_round}/{self.total_rounds})", True, (255, 0, 0))
        else:
            round_text = self.small_font.render(f"Round: {self.current_round}/{self.total_rounds}", True, BLACK)
        
        round_rect = round_text.get_rect(topleft=(10, SCREEN_HEIGHT - 30))
        self.screen.blit(round_text, round_rect)
        
        # Draw game over screen if applicable
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            if self.win:
                result_text = self.font.render("You Won!", True, WHITE)
            else:
                result_text = self.font.render("Game Over", True, WHITE)
                
            continue_text = self.small_font.render("Press any key to continue", True, WHITE)
            
            result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            
            self.screen.blit(result_text, result_rect)
            self.screen.blit(continue_text, continue_rect)
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                
                if self.game_over:
                    if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                        if self.current_round <= self.total_rounds:
                            self.reset_round()
                            self.game_over = False
                        else:
                            running = False
                else:
                    self.handle_event(event)
            
            # Update cat positions for animation
            self.update_cats()
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='9 Lives - Math Game')
    parser.add_argument('--round', '-r', type=int, default=1, 
                        help='Start at a specific round (1-9)')
    args = parser.parse_args()
    
    # Validate round number
    start_round = max(1, min(9, args.round))  # Clamp between 1 and 9
    
    game = NineLives()
    # Set the starting round
    game.current_round = start_round
    game.reset_round()
    game.run() 