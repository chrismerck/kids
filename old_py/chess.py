import pygame
import os
import sys
import copy
from enum import Enum, auto

# Initialize pygame
pygame.init()

# Constants
SQUARE_SIZE = 50
BOARD_WIDTH = 16 * SQUARE_SIZE  # 8 + 4 + 4 squares wide
BOARD_HEIGHT = 16 * SQUARE_SIZE  # 8 + 4 + 4 squares high
SCREEN_WIDTH = BOARD_WIDTH + 200  # Extra space for UI
SCREEN_HEIGHT = BOARD_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_SQUARE = (118, 150, 86)
LIGHT_SQUARE = (238, 238, 210)
HIGHLIGHT = (186, 202, 68)
PLAYER_COLORS = {
    'north': (220, 20, 60),   # Red
    'east': (65, 105, 225),   # Royal Blue
    'south': (255, 215, 0),   # Gold
    'west': (34, 139, 34)     # Forest Green
}

class Player(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()

class PieceType(Enum):
    PAWN = auto()
    KNIGHT = auto()
    BISHOP = auto()
    ROOK = auto()
    QUEEN = auto()
    KING = auto()

class Piece:
    def __init__(self, piece_type, player, row, col):
        self.type = piece_type
        self.player = player
        self.row = row
        self.col = col
        self.has_moved = False
        self.character = self.get_character()
    
    def get_character(self):
        # Simple letter representation of chess pieces
        chars = {
            PieceType.KING: 'K',
            PieceType.QUEEN: 'Q',
            PieceType.ROOK: 'R',
            PieceType.BISHOP: 'B',
            PieceType.KNIGHT: 'N',
            PieceType.PAWN: 'P'
        }
        return chars[self.type]
    
    def move(self, row, col):
        self.row = row
        self.col = col
        self.has_moved = True
    
    def get_valid_moves(self, board):
        # Get valid moves based on piece type
        valid_moves = []
        
        if self.type == PieceType.PAWN:
            valid_moves = self._get_pawn_moves(board)
        elif self.type == PieceType.KNIGHT:
            valid_moves = self._get_knight_moves(board)
        elif self.type == PieceType.BISHOP:
            valid_moves = self._get_bishop_moves(board)
        elif self.type == PieceType.ROOK:
            valid_moves = self._get_rook_moves(board)
        elif self.type == PieceType.QUEEN:
            valid_moves = self._get_queen_moves(board)
        elif self.type == PieceType.KING:
            valid_moves = self._get_king_moves(board)
        
        return valid_moves
    
    def _get_pawn_moves(self, board):
        valid_moves = []
        row, col = self.row, self.col
        
        # Define movement direction based on player
        if self.player == Player.NORTH:
            direction = 1  # Moving down
            starting_row = 1
        elif self.player == Player.EAST:
            direction = -1  # Moving left
            starting_row = 14
        elif self.player == Player.SOUTH:
            direction = -1  # Moving up
            starting_row = 14
        else:  # Player.WEST
            direction = 1  # Moving right
            starting_row = 1
        
        # Determine which axis the pawn moves along
        if self.player in [Player.NORTH, Player.SOUTH]:
            # Forward move
            next_row = row + direction
            if board.is_valid_position(next_row, col) and board.get_piece(next_row, col) is None:
                valid_moves.append((next_row, col))
                
                # Double move from starting position
                if row == starting_row:
                    next_row = row + 2 * direction
                    if board.is_valid_position(next_row, col) and board.get_piece(next_row, col) is None:
                        valid_moves.append((next_row, col))
            
            # Captures
            for c_offset in [-1, 1]:
                next_col = col + c_offset
                next_row = row + direction
                if board.is_valid_position(next_row, next_col):
                    piece = board.get_piece(next_row, next_col)
                    if piece and piece.player != self.player:
                        valid_moves.append((next_row, next_col))
        else:  # Player.EAST or Player.WEST
            # Forward move
            next_col = col + direction
            if board.is_valid_position(row, next_col) and board.get_piece(row, next_col) is None:
                valid_moves.append((row, next_col))
                
                # Double move from starting position
                if col == starting_row:  # Using row variable for column in this context
                    next_col = col + 2 * direction
                    if board.is_valid_position(row, next_col) and board.get_piece(row, next_col) is None:
                        valid_moves.append((row, next_col))
            
            # Captures
            for r_offset in [-1, 1]:
                next_row = row + r_offset
                next_col = col + direction
                if board.is_valid_position(next_row, next_col):
                    piece = board.get_piece(next_row, next_col)
                    if piece and piece.player != self.player:
                        valid_moves.append((next_row, next_col))
        
        return valid_moves
    
    def _get_knight_moves(self, board):
        valid_moves = []
        row, col = self.row, self.col
        
        # Knights move in L-shape: 2 squares in one direction, 1 square perpendicular
        knight_moves = [
            (-2, -1), (-2, 1),  # Up 2, left/right 1
            (-1, -2), (-1, 2),  # Up 1, left/right 2
            (1, -2), (1, 2),    # Down 1, left/right 2
            (2, -1), (2, 1)     # Down 2, left/right 1
        ]
        
        for move in knight_moves:
            next_row = row + move[0]
            next_col = col + move[1]
            
            if board.is_valid_position(next_row, next_col):
                piece = board.get_piece(next_row, next_col)
                # Can move to empty square or capture opponent's piece
                if piece is None or piece.player != self.player:
                    valid_moves.append((next_row, next_col))
        
        return valid_moves
    
    def _get_bishop_moves(self, board):
        valid_moves = []
        row, col = self.row, self.col
        
        # Bishops move diagonally
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for direction in directions:
            for i in range(1, 16):  # Maximum board size
                next_row = row + direction[0] * i
                next_col = col + direction[1] * i
                
                if not board.is_valid_position(next_row, next_col):
                    break
                
                piece = board.get_piece(next_row, next_col)
                if piece is None:
                    valid_moves.append((next_row, next_col))
                elif piece.player != self.player:
                    valid_moves.append((next_row, next_col))
                    break
                else:
                    break
        
        return valid_moves
    
    def _get_rook_moves(self, board):
        valid_moves = []
        row, col = self.row, self.col
        
        # Rooks move horizontally and vertically
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        for direction in directions:
            for i in range(1, 16):  # Maximum board size
                next_row = row + direction[0] * i
                next_col = col + direction[1] * i
                
                if not board.is_valid_position(next_row, next_col):
                    break
                
                piece = board.get_piece(next_row, next_col)
                if piece is None:
                    valid_moves.append((next_row, next_col))
                elif piece.player != self.player:
                    valid_moves.append((next_row, next_col))
                    break
                else:
                    break
        
        return valid_moves
    
    def _get_queen_moves(self, board):
        # Queen combines bishop and rook movements
        bishop_moves = self._get_bishop_moves(board)
        rook_moves = self._get_rook_moves(board)
        return bishop_moves + rook_moves
    
    def _get_king_moves(self, board):
        valid_moves = []
        row, col = self.row, self.col
        
        # Kings move one square in any direction
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for direction in directions:
            next_row = row + direction[0]
            next_col = col + direction[1]
            
            if board.is_valid_position(next_row, next_col):
                piece = board.get_piece(next_row, next_col)
                if piece is None or piece.player != self.player:
                    valid_moves.append((next_row, next_col))
        
        return valid_moves

class GameState:
    def __init__(self, board, current_player):
        self.board_grid = copy.deepcopy(board.grid)
        self.current_player = current_player

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(16)] for _ in range(16)]
        self.setup_pieces()
    
    def setup_pieces(self):
        # North player (red)
        self._setup_player_pieces(Player.NORTH)
        
        # East player (blue)
        self._setup_player_pieces(Player.EAST)
        
        # South player (gold)
        self._setup_player_pieces(Player.SOUTH)
        
        # West player (green)
        self._setup_player_pieces(Player.WEST)
    
    def _setup_player_pieces(self, player):
        # Set up pieces based on player position
        if player == Player.NORTH:
            # Back row (row 0)
            self.grid[0][4] = Piece(PieceType.ROOK, player, 0, 4)
            self.grid[0][5] = Piece(PieceType.KNIGHT, player, 0, 5)
            self.grid[0][6] = Piece(PieceType.BISHOP, player, 0, 6)
            self.grid[0][7] = Piece(PieceType.QUEEN, player, 0, 7)
            self.grid[0][8] = Piece(PieceType.KING, player, 0, 8)
            self.grid[0][9] = Piece(PieceType.BISHOP, player, 0, 9)
            self.grid[0][10] = Piece(PieceType.KNIGHT, player, 0, 10)
            self.grid[0][11] = Piece(PieceType.ROOK, player, 0, 11)
            
            # Pawns (row 1)
            for col in range(4, 12):
                self.grid[1][col] = Piece(PieceType.PAWN, player, 1, col)
                
        elif player == Player.EAST:
            # Back row (column 15)
            self.grid[4][15] = Piece(PieceType.ROOK, player, 4, 15)
            self.grid[5][15] = Piece(PieceType.KNIGHT, player, 5, 15)
            self.grid[6][15] = Piece(PieceType.BISHOP, player, 6, 15)
            self.grid[7][15] = Piece(PieceType.QUEEN, player, 7, 15)
            self.grid[8][15] = Piece(PieceType.KING, player, 8, 15)
            self.grid[9][15] = Piece(PieceType.BISHOP, player, 9, 15)
            self.grid[10][15] = Piece(PieceType.KNIGHT, player, 10, 15)
            self.grid[11][15] = Piece(PieceType.ROOK, player, 11, 15)
            
            # Pawns (column 14)
            for row in range(4, 12):
                self.grid[row][14] = Piece(PieceType.PAWN, player, row, 14)
                
        elif player == Player.SOUTH:
            # Back row (row 15)
            self.grid[15][4] = Piece(PieceType.ROOK, player, 15, 4)
            self.grid[15][5] = Piece(PieceType.KNIGHT, player, 15, 5)
            self.grid[15][6] = Piece(PieceType.BISHOP, player, 15, 6)
            self.grid[15][7] = Piece(PieceType.KING, player, 15, 7)
            self.grid[15][8] = Piece(PieceType.QUEEN, player, 15, 8)
            self.grid[15][9] = Piece(PieceType.BISHOP, player, 15, 9)
            self.grid[15][10] = Piece(PieceType.KNIGHT, player, 15, 10)
            self.grid[15][11] = Piece(PieceType.ROOK, player, 15, 11)
            
            # Pawns (row 14)
            for col in range(4, 12):
                self.grid[14][col] = Piece(PieceType.PAWN, player, 14, col)
                
        elif player == Player.WEST:
            # Back row (column 0)
            self.grid[4][0] = Piece(PieceType.ROOK, player, 4, 0)
            self.grid[5][0] = Piece(PieceType.KNIGHT, player, 5, 0)
            self.grid[6][0] = Piece(PieceType.BISHOP, player, 6, 0)
            self.grid[7][0] = Piece(PieceType.KING, player, 7, 0)
            self.grid[8][0] = Piece(PieceType.QUEEN, player, 8, 0)
            self.grid[9][0] = Piece(PieceType.BISHOP, player, 9, 0)
            self.grid[10][0] = Piece(PieceType.KNIGHT, player, 10, 0)
            self.grid[11][0] = Piece(PieceType.ROOK, player, 11, 0)
            
            # Pawns (column 1)
            for row in range(4, 12):
                self.grid[row][1] = Piece(PieceType.PAWN, player, row, 1)
    
    def is_valid_position(self, row, col):
        # Check if the position is within the board boundaries
        if 0 <= row < 16 and 0 <= col < 16:
            # Check if the position is part of the playable area
            # Center 8x8
            if 4 <= row < 12 and 4 <= col < 12:
                return True
            # North area (4x8)
            elif 0 <= row < 4 and 4 <= col < 12:
                return True
            # East area (8x4)
            elif 4 <= row < 12 and 12 <= col < 16:
                return True
            # South area (4x8)
            elif 12 <= row < 16 and 4 <= col < 12:
                return True
            # West area (8x4)
            elif 4 <= row < 12 and 0 <= col < 4:
                return True
        return False
    
    def get_piece(self, row, col):
        if self.is_valid_position(row, col):
            return self.grid[row][col]
        return None
    
    def move_piece(self, from_row, from_col, to_row, to_col):
        piece = self.get_piece(from_row, from_col)
        if piece:
            self.grid[to_row][to_col] = piece
            self.grid[from_row][from_col] = None
            piece.move(to_row, to_col)
            return True
        return False
    
    def copy_from_grid(self, grid):
        """Create a new board state from a grid"""
        self.grid = copy.deepcopy(grid)
        
        # Update the row and col attributes of each piece to match their position in the grid
        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                piece = self.grid[row][col]
                if piece:
                    piece.row = row
                    piece.col = col

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("4-Player Chess")
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.current_player = Player.NORTH
        self.selected_piece = None
        self.valid_moves = []
        self.move_history = []  # Store game state history
        
        # Save initial state
        self.save_game_state()
        
        # Try to find a font that supports Unicode chess symbols
        # If you want to attempt Unicode again, try these fonts instead of Arial
        available_fonts = pygame.font.get_fonts()
        font_options = ['dejavusans', 'segoeuisymbol', 'symbola', 'arial unicode ms']
        
        chosen_font = None
        for font in font_options:
            if font in available_fonts:
                chosen_font = font
                break
        
        if chosen_font:
            self.font = pygame.font.SysFont(chosen_font, 40)  # Font for chess pieces
        else:
            self.font = pygame.font.SysFont('Arial', 40)  # Fallback to Arial
        
        self.ui_font = pygame.font.SysFont('Arial', 24)  # Font for UI
        
    def save_game_state(self):
        """Save the current game state to history"""
        state = GameState(self.board, self.current_player)
        self.move_history.append(state)
    
    def undo_move(self):
        """Undo the last move by restoring previous game state"""
        if len(self.move_history) > 1:  # Keep at least the initial state
            # Remove the current state
            self.move_history.pop()
            
            # Get the previous state
            previous_state = self.move_history[-1]
            
            # Restore the board
            self.board.copy_from_grid(previous_state.board_grid)
            
            # Restore the current player
            self.current_player = previous_state.current_player
            
            # Clear selection
            self.selected_piece = None
            self.valid_moves = []
    
    def draw_board(self):
        self.screen.fill(BLACK)
        
        # Draw all squares that are part of the playable area
        for row in range(16):
            for col in range(16):
                if self.board.is_valid_position(row, col):
                    color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                    pygame.draw.rect(self.screen, color, 
                                    (col * SQUARE_SIZE, row * SQUARE_SIZE, 
                                     SQUARE_SIZE, SQUARE_SIZE))
        
        # Draw pieces
        for row in range(16):
            for col in range(16):
                piece = self.board.get_piece(row, col)
                if piece:
                    # Get player color
                    player_name = piece.player.name.lower()
                    color = PLAYER_COLORS[player_name]
                    
                    # Create a circle in the player's color as background
                    circle_center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, 
                                   row * SQUARE_SIZE + SQUARE_SIZE // 2)
                    circle_radius = SQUARE_SIZE // 2 - 5
                    pygame.draw.circle(self.screen, color, circle_center, circle_radius)
                    
                    # Draw the character in white or black (for contrast)
                    # Choose text color based on background brightness
                    r, g, b = color
                    brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                    text_color = BLACK if brightness > 0.5 else WHITE
                    
                    # Render the character
                    text = self.font.render(piece.character, True, text_color)
                    text_rect = text.get_rect(center=circle_center)
                    self.screen.blit(text, text_rect)
        
        # Highlight selected piece and valid moves
        if self.selected_piece:
            row, col = self.selected_piece.row, self.selected_piece.col
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill((255, 255, 0, 128))  # Transparent yellow
            self.screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            
            for move_row, move_col in self.valid_moves:
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill((0, 255, 0, 128))  # Transparent green
                self.screen.blit(s, (move_col * SQUARE_SIZE, move_row * SQUARE_SIZE))
        
        # Draw UI elements
        # Current player indicator
        player_name = self.current_player.name
        color = PLAYER_COLORS[player_name.lower()]
        text = self.ui_font.render(f"Current Player: {player_name}", True, color)
        self.screen.blit(text, (BOARD_WIDTH + 10, 20))
        
        # Add UI for undo
        undo_text = self.ui_font.render("Press BACKSPACE to Undo", True, WHITE)
        self.screen.blit(undo_text, (BOARD_WIDTH + 10, 60))
        
        pygame.display.flip()
    
    def handle_click(self, row, col):
        if not self.board.is_valid_position(row, col):
            return
        
        piece = self.board.get_piece(row, col)
        
        # If a piece is already selected and a valid move is clicked
        if self.selected_piece and (row, col) in self.valid_moves:
            # Move the selected piece
            self.board.move_piece(self.selected_piece.row, self.selected_piece.col, row, col)
            self.selected_piece = None
            self.valid_moves = []
            
            # Change to next player
            self.next_turn()
            
            # Save the state AFTER completing the move and changing the player
            self.save_game_state()
        # If clicking on own piece, select it
        elif piece and piece.player == self.current_player:
            self.selected_piece = piece
            self.valid_moves = piece.get_valid_moves(self.board)
        # If clicking elsewhere, deselect
        else:
            self.selected_piece = None
            self.valid_moves = []
    
    def next_turn(self):
        # Cycle through players
        if self.current_player == Player.NORTH:
            self.current_player = Player.EAST
        elif self.current_player == Player.EAST:
            self.current_player = Player.SOUTH
        elif self.current_player == Player.SOUTH:
            self.current_player = Player.WEST
        else:
            self.current_player = Player.NORTH
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_pos = pygame.mouse.get_pos()
                        col = mouse_pos[0] // SQUARE_SIZE
                        row = mouse_pos[1] // SQUARE_SIZE
                        self.handle_click(row, col)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.undo_move()
            
            self.draw_board()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
