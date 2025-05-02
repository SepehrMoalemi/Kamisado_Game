# Purpose: Handle GUI
# %------------------------------------------ Packages -------------------------------------------% #
import pygame
from dataclasses import dataclass
# %------------------------------------------- Structs -------------------------------------------% #
@dataclass
class Settings:
    DIM       : int
    LENGTH    : int
    CELL_SIZE : int  
    MAX_FPS   : int
    BOARD_STARTING_COLOR : str = "default"
    BOARD_PIECE_SHAPE    : str = "simple_circle"
    
# %--------------------------------------- Global Settings ---------------------------------------% #
COLOR_MAP = {
    "orange": (255, 105, 0),
    "blue": (0, 0, 255),
    "purple": (128, 0, 128),
    "pink": (255, 16, 240),
    "yellow": (255, 255, 0),
    "red": (255, 0, 0),
    "green": (0, 128, 0),
    "brown": (165, 42, 42),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "gold": (255, 215, 0),
    "gray": (128, 128, 128),
}
    
# %------------------------------------------ GUI Classes ----------------------------------------% #
class Window():
    def __init__(self, Game, SETTINGS : Settings) -> None:
        self.Game = Game
        self.SETTINGS = SETTINGS 
        
        # Initialize Pygame
        pygame.init()
        pygame.display.set_caption("Kamisado!")
        
        # Setup Screen
        self.screen = pygame.display.set_mode((self.SETTINGS.LENGTH,
                                               self.SETTINGS.LENGTH),
                                               pygame.RESIZABLE)
        # Setup Clock
        self.clock  = pygame.time.Clock()
        
        # Setup Board themes
        self.BOARD_COLORS = self.get_board_colors()
        self.PIECE_SHAPE  = self.get_piece_theme()
        
        # Initialize Board bitmap
        self.piece_bitmap, self.EMPTY_SQUARE = self.get_initial_piece_bitmap()
        self.PIECE_ID_TO_POSITION, self.PIECE_ID_TO_COLOR, self.PIECE_COLOR_TO_ID = self.get_piece_maps()
        
        # Piece Click Handler
        self.last_moved_piece_pos   = None   # (row, col) of last moved piece
        self.selected_piece_pos     = None   # (row, col) of currently selected piece
        self.next_piece_to_move_pos = None   # (row, col) of next piece to move
        self.dragging_piece_pos     = None   # (row, col) of piece being dragged
        
        # Game ending
        self.game_over = False

    # Purpose: resize Window based on User Event
    def resize(self, event) -> None:
        # Resize the window to smallest dimension to keep it square
        self.SETTINGS.LENGTH = min(event.w, event.h)
        self.SETTINGS.CELL_SIZE = self.SETTINGS.LENGTH // self.SETTINGS.DIM
        self.screen = pygame.display.set_mode((self.SETTINGS.LENGTH, self.SETTINGS.LENGTH),
                                               pygame.RESIZABLE)
        
    # Purpose: Render Window
    def render_window(self) -> None:
        self.clock.tick(self.SETTINGS.MAX_FPS)
        pygame.display.update()

    # Purpose: Render Board
    def render_background(self) -> None:
        cs = self.SETTINGS.CELL_SIZE
        for r in range(self.SETTINGS.DIM):
            for c in range(self.SETTINGS.DIM):
                color = self.BOARD_COLORS[r][c]
                pygame.draw.rect(self.screen, color,
                                 pygame.Rect(c * cs, r * cs, 
                                                 cs,     cs))
                
    # Purpose: Render Pieces
    def render_pieces(self):
        for row in range(self.SETTINGS.DIM):
            for col in range(self.SETTINGS.DIM):
                piece_id = self.piece_bitmap[row][col]
                if piece_id != self.EMPTY_SQUARE:
                    # Skip rendering the piece if it is being dragged
                    if self.dragging_piece_pos == (row, col):
                        continue
                    self.PIECE_SHAPE(self.SETTINGS.CELL_SIZE, row, col, piece_id=piece_id)

    # Purpose: Render Selection Highlighting
    def render_selection_highlighting(self, piece):
        if piece:
            self.PIECE_SHAPE(self.SETTINGS.CELL_SIZE, *piece, IS_SELECTED=True)
    
    # Purpose: Render Dragging Piece
    def render_dragging_piece(self):
        if self.dragging_piece_pos:
            # Get the current mouse position
            x, y = pygame.mouse.get_pos()
            cs   = self.SETTINGS.CELL_SIZE
            
            # Get piece ID to render
            row, col = self.dragging_piece_pos
            piece_id = self.piece_bitmap[row][col]
            self.selected_piece_pos = None
            
            # Draw piece and selection ring
            self.PIECE_SHAPE(cs, row, col, piece_id, drag_coords=(x, y))
            self.PIECE_SHAPE(cs, row, col, piece_id, drag_coords=(x, y), IS_SELECTED=True)
       
    # Purpose: Render All Legal Moves
    def render_legal_moves(self):
        cs = self.SETTINGS.CELL_SIZE
        
        # Draw circles for each legal move
        radius = cs // 10
        for row, col in self.Game.cached_legal_moves:
            center = (col * cs + cs // 2, row * cs + cs // 2)
            pygame.draw.circle(self.screen, COLOR_MAP["gray"], center, radius)
            pygame.draw.circle(self.screen, COLOR_MAP["black"], center, radius + 1, width=2)
            
    # Purpose: Display game over screen
    def render_game_over(self):
        if self.game_over:
            if self.Game.turn_skipped:
                # Currently turn skip condition is checked after turn is passed:
                # So the winner is the player who just passed their turn
                WINNER = "Black" if self.Game.turn_player == self.Game.BLACK_PLAYER else "White"
            else:
                WINNER = "White" if self.Game.turn_player == self.Game.BLACK_PLAYER else "Black"
            font_size = int(self.SETTINGS.CELL_SIZE * 0.6)
            font = pygame.font.SysFont(None, font_size)
            text_surface = font.render(f"Game Over - {WINNER} Wins!", True, (0, 0, 0), (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.SETTINGS.LENGTH // 2, self.SETTINGS.LENGTH // 2))
            self.screen.blit(text_surface, text_rect)

    # Purpose: Render the Entire Board + Pieces
    def render_board(self) -> None:
        self.render_background()
        self.render_pieces()
        if not self.game_over:
            self.render_legal_moves()
            self.render_dragging_piece()
            self.render_selection_highlighting(self.last_moved_piece_pos)
            self.render_selection_highlighting(self.selected_piece_pos)
            self.render_selection_highlighting(self.next_piece_to_move_pos)
        self.render_game_over()
        self.render_window()
        
    # Purpose: Handle Mouse Dragging
    def handle_mouse_down(self, pos):
        # Stop handling input if game is over
        if self.game_over:
            return
        
        # Get row and col from mouse position
        row, col = self.get_row_col_from_mouse_pos(pos)
        
        # Click outside board, ignore
        if not self.move_is_in_bounds(row, col):
            return
        
        # If clicked piece is not the next piece to move, ignore
        if self.next_piece_to_move_pos and (row, col) != self.next_piece_to_move_pos:
            return

        # Determin Clicked piece
        clicked_piece = self.piece_bitmap[row][col]
        
        # Start dragging if clicked on your own piece
        if clicked_piece * self.Game.turn_player > 0:
            self.selected_piece_pos = (row, col)
            self.dragging_piece_pos = (row, col)
            self.Game.set_cached_legal_moves(self.selected_piece_pos)
        
    # Purpose: Handle Mouse Dragging
    def handle_mouse_up(self, pos):
        # Stop handling input if game is over
        if self.game_over:
            return
        
        # Get row and col from mouse position
        row, col = self.get_row_col_from_mouse_pos(pos)

        # Click outside board, ignore
        if not self.move_is_in_bounds(row, col):
            return

        # Handle dragging piece
        if self.dragging_piece_pos:
            start_row, start_col = self.dragging_piece_pos
            clicked_piece = self.piece_bitmap[row][col]

            # CASE 1: Dragging to empty square
            if clicked_piece == self.EMPTY_SQUARE:
                # Check if move is valid
                if (row, col) in self.Game.cached_legal_moves:
                    # Reset skip turn since a valid can be made
                    self.Game.turn_skipped = False
                    
                    # Move piece
                    moving_piece_id = self.piece_bitmap[start_row][start_col]
                    self.piece_bitmap[row][col] = moving_piece_id
                    self.PIECE_ID_TO_POSITION[moving_piece_id] = (row, col)
                    self.piece_bitmap[start_row][start_col] = self.EMPTY_SQUARE
                        
                    # Check for game over
                    if self.Game.check_for_game_end_back_rank(row):
                        self.game_over = True
                        
                    # Update last moved piece position and pass turn
                    self.update_lcn_piece_pos(row, col)
                    self.Game.pass_turn()
                        
            # CASE 2: Released back on your own piece
            elif (row, col) == (start_row, start_col):
                # Deselect the piece if released on the same square
                if self.selected_piece_pos == (row, col):
                    self.selected_piece_pos = None
                else:
                    # Check for skip turn
                    if len(self.Game.cached_legal_moves) == 0:
                        # Check for turn skip loop
                        if self.Game.check_for_game_end_loop(clicked_piece):
                            self.game_over = True
                        
                        # Skip turn
                        self.update_lcn_piece_pos(row, col)
                        self.Game.pass_turn()
                        self.Game.turn_skipped = True
                    # Select piece
                    else:
                        self.selected_piece_pos = (row, col)
        else:
            # No dragging, just clicked
            clicked_piece = self.piece_bitmap[row][col]
            
            # CASE 1: Clicked your own piece
            if clicked_piece * self.Game.turn_player > 0:
                if self.selected_piece_pos == (row, col):
                    self.selected_piece_pos = None
                else:
                    # If clicked piece is not the next piece to move, ignore
                    if self.next_piece_to_move_pos and (row, col) != self.next_piece_to_move_pos:
                        return
                    # Check if the piece has legal moves
                    if len(self.Game.cached_legal_moves) == 0:
                        # Check for turn skip loop
                        if self.Game.check_for_game_end_loop(clicked_piece):
                            self.game_over = True
                            
                        # Skip turn
                        self.update_lcn_piece_pos(row, col)
                        self.Game.pass_turn()
                        self.Game.turn_skipped = True
                    else:
                        self.selected_piece_pos = (row, col)

            # CASE 2: Clicked empty square while a piece is selected
            elif clicked_piece == self.EMPTY_SQUARE and self.selected_piece_pos:
                # Get the piece ID from position
                sel_row, sel_col = self.selected_piece_pos
                moving_piece_id = self.piece_bitmap[sel_row][sel_col]

                # Move piece
                if (row, col) in self.Game.cached_legal_moves:
                    self.Game.turn_skipped = False
                    self.piece_bitmap[row][col] = moving_piece_id
                    self.PIECE_ID_TO_POSITION[moving_piece_id] = (row, col)
                    self.piece_bitmap[sel_row][sel_col] = self.EMPTY_SQUARE

                    # Check for game over
                    if self.Game.check_for_game_end_back_rank(row):
                        self.game_over = True
                        
                    # Update last moved piece position and pass turn
                    self.update_lcn_piece_pos(row, col)
                    self.Game.pass_turn()
                    
        # Always reset drag state after mouse up
        self.dragging_piece_pos = None
        
    # Purpose: Check if move is in bounds
    def move_is_in_bounds(self, row, col):
        return 0 <= row < self.SETTINGS.DIM and 0 <= col < self.SETTINGS.DIM
    
    # Purpose: Check if square is empty
    def square_is_empty(self, row, col):
        return self.piece_bitmap[row][col] == self.EMPTY_SQUARE
    
    # Purpose: Update last/current/next piece to move
    def update_lcn_piece_pos(self, row, col):
        # Update last moved piece position
        self.last_moved_piece_pos = (row, col)
        
        # Find the RGB color at the landing square
        color = self.BOARD_COLORS[row][col]

        # Find which piece corresponds to that color for the current player
        piece_id = self.PIECE_COLOR_TO_ID[self.Game.turn_player][color]
        self.next_piece_to_move_pos = self.PIECE_ID_TO_POSITION[piece_id]
        self.selected_piece_pos = self.next_piece_to_move_pos
        
    # Purpose: Get row and col from mouse position
    def get_row_col_from_mouse_pos(self, pos):
        x, y = pos
        col = x // self.SETTINGS.CELL_SIZE
        row = y // self.SETTINGS.CELL_SIZE
        return row, col
    
    # Purpose: Get Piece Theme/shape
    def get_piece_theme(self):
        match self.SETTINGS.BOARD_PIECE_SHAPE:
            case "simple_circle":
                return self.piece_theme_simple_circle
            
            case "rooks":
                return self.piece_theme_rooks
            
            case _:
                raise NotImplementedError("This is not implemented yet")
    
    # Purpose: Draw rooks
    def piece_theme_rooks(self, cs, row, col, piece_id = 1, IS_SELECTED = False, drag_coords = None):
        surface = self.screen
        color_main = COLOR_MAP["black"] if piece_id > 0 else COLOR_MAP["white"]
        color_ring = self.PIECE_ID_TO_COLOR[piece_id]

        # Calculate center and base size
        if drag_coords:
            cx, cy = drag_coords
        else:
            cx = col * cs + cs // 2
            cy = row * cs + cs // 2

        base_width        = cs // 2
        tower_height      = cs // 2
        battlement_height = cs // 8
        segment_width     = cs // 9 

        # Main tower rectangle
        tower_rect = pygame.Rect(0, 0, base_width, tower_height)
        tower_rect.center = (cx, cy)
        
        # Optional selection ring
        if IS_SELECTED:
            pygame.draw.circle(surface, COLOR_MAP["gold"], (cx, cy), cs // 2, width=2)
            pygame.draw.circle(surface, COLOR_MAP["black"], (cx, cy), cs // 2 + 1, width=1)
        else:
            # Draw main tower
            pygame.draw.rect(surface, color_main, tower_rect)

            # Top battlements (aligned left, center, right)
            top_y = tower_rect.top
            battlements = [
                (cx - base_width // 2, top_y - battlement_height),                 # left
                (cx - segment_width // 2, top_y - battlement_height),              # center
                (cx + base_width // 2 - segment_width, top_y - battlement_height)  # right
            ]
            
            for x, y in battlements:
                rect = pygame.Rect(x, y, segment_width, battlement_height)
                pygame.draw.rect(surface, color_main, rect)
                pygame.draw.rect(surface, COLOR_MAP["black"], rect, width=1)

            # Add colored circle in the middle
            pygame.draw.circle(surface, color_ring, (cx, cy), cs // 6)
            pygame.draw.circle(surface, COLOR_MAP["black"], (cx, cy), cs // 6, width=1)

            # Draw tower outline
            pygame.draw.rect(surface, COLOR_MAP["black"], tower_rect, width=1)
    
    # Purpose: Draw a simple circle piece
    def piece_theme_simple_circle(self, cs, row, col, piece_id = 1, IS_SELECTED = False, drag_coords = None):
            radius = cs // 3
            color_radius = cs // 5
            if drag_coords:
                center = drag_coords
            else:
                center = (col * cs + cs // 2, 
                          row * cs + cs // 2)
            if IS_SELECTED:
                pygame.draw.circle(self.screen, COLOR_MAP["gold"], center, radius + 2, width=2)
                pygame.draw.circle(self.screen, COLOR_MAP["black"], center, radius + 3, width=1)
            else:
                color = COLOR_MAP["black"] if piece_id > 0 else COLOR_MAP["white"]
                pygame.draw.circle(self.screen, color, center, radius)
                pygame.draw.circle(self.screen, self.PIECE_ID_TO_COLOR[piece_id], center, color_radius)
                pygame.draw.circle(self.screen, COLOR_MAP["black"], center, radius, width=1)
                pygame.draw.circle(self.screen, COLOR_MAP["black"], center, color_radius, width=1)
                
    # Purpose: Initialize Board bitmap 
    def get_initial_piece_bitmap(self):
        DIM = self.SETTINGS.DIM
        EMPTY_SQUARE = 0
        
        # Populate the board
        board = [[EMPTY_SQUARE for _ in range(DIM)] for _ in range(DIM)]
        for c in range(DIM):
            # Assign pieces to the first and last rows
            board[0][c] = c + 1     # Black pieces: 1, 2, 3, ..., 8
            board[-1][c] = -(c + 1) # White pieces: -1, -2, -3, ..., -8
        return board, EMPTY_SQUARE
    
    # Purpose: Get Piece Maps to color and position
    def get_piece_maps(self):
        DIM = self.SETTINGS.DIM
        PIECE_ID_TO_POSITION = {}
        PIECE_ID_TO_COLOR = {}
        PIECE_COLOR_TO_ID = {}
        PIECE_COLOR_TO_ID_White = {}
        PIECE_COLOR_TO_ID_Black = {}
        for c in range(DIM):
            # Assign postion to piece IDs
            PIECE_ID_TO_POSITION[c + 1] = (0, c)
            PIECE_ID_TO_POSITION[-(c + 1)] = (DIM - 1, c)
            
            # Assign colors to piece IDs
            PIECE_ID_TO_COLOR[c + 1] = self.BOARD_COLORS[0][c]
            PIECE_ID_TO_COLOR[-(c + 1)] = self.BOARD_COLORS[-1][c]
            
            # Assign piece IDs to colors
            PIECE_COLOR_TO_ID_Black[self.BOARD_COLORS[0][c]] = c + 1
            PIECE_COLOR_TO_ID_White[self.BOARD_COLORS[-1][c]] = -(c + 1)
        PIECE_COLOR_TO_ID[-1] = PIECE_COLOR_TO_ID_Black
        PIECE_COLOR_TO_ID[1] = PIECE_COLOR_TO_ID_White
        return PIECE_ID_TO_POSITION, PIECE_ID_TO_COLOR, PIECE_COLOR_TO_ID
        
    # Purpose: Get Board Square Colors
    def get_board_colors(self):
        default_board_colors = [
            ["orange", "blue",   "purple", "pink",   "yellow", "red",    "green",  "brown"],
            ["red",    "orange", "pink",   "green",  "blue",   "yellow", "brown",  "purple"],
            ["green",  "pink",   "orange", "red",    "purple", "brown",  "yellow", "blue"],
            ["pink",   "purple", "blue",   "orange", "brown",  "green",  "red",    "yellow"],
            ["yellow", "red",    "green",  "brown",  "orange", "blue",   "purple", "pink"],
            ["blue",   "yellow", "brown",  "purple", "red",    "orange", "pink",   "green"],
            ["purple", "brown",  "yellow", "blue",   "green",  "pink",   "orange", "red"],
            ["brown",  "green",  "red",    "yellow", "pink",   "purple", "blue",   "orange"],
        ]
        match self.SETTINGS.BOARD_STARTING_COLOR:
            case "default":
                board_colors = default_board_colors
            case "rotate 90":
                board_colors = [list(row)[::-1] for row in zip(*default_board_colors)]
            case "rotate 180":
                board_colors = [row[::-1] for row in default_board_colors[::-1]]
            case "rotate 270":
                board_colors = [list(row) for row in zip(*default_board_colors)][::-1]
            case _:
                raise NotImplementedError("This is not implemented yet")
        return [[COLOR_MAP[color] for color in row] for row in board_colors]