# Purpose: Game Rules and Setup
# %------------------------------------------ Packages ------------------------------------% #
import board
import pygame
# %---------------------------------------- Game Classes ----------------------------------% #
class Kamisado():
    def __init__(self, SETTINGS) -> None:
        # Setup GUI
        self.Board = board.Window(self, SETTINGS)
        
        # Game Player setup
        self.WHITE_PLAYER = -1                      # Used to identify the player
        self.BLACK_PLAYER = 1                       # Used to identify the player
        self.turn_player  = self.WHITE_PLAYER 
        self.turn_skipped = False                   # Turn skip if no legal moves
        self.cached_legal_moves = []                # Cache legal moves for current piece
        
    # Purpose: run Game
    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                match event.type:
                    # Stop Game
                    case pygame.QUIT:
                        running = False
                        
                    # Scale Board
                    case pygame.VIDEORESIZE:
                        self.Board.resize(event)
                        
                    # Handle Click
                    case pygame.MOUSEBUTTONDOWN:
                        self.Board.handle_mouse_down(event.pos)

                    case pygame.MOUSEBUTTONUP:
                        self.Board.handle_mouse_up(event.pos)
            self.Board.render_board()
            
    # Purpose: Pass Turn to the other player
    def pass_turn(self):
        # Update turn player 
        self.turn_player = self.BLACK_PLAYER if self.turn_player == self.WHITE_PLAYER else self.WHITE_PLAYER
        
        # Determine the legal moves
        self.cached_legal_moves = self.get_legal_moves(self.Board.next_piece_to_move_pos)
        
    
    # Purpose: Get the legal moves for a piece
    def get_legal_moves(self, piece_pos):
        # Determine the piece to move
        row, col = piece_pos
        piece_id = self.Board.piece_bitmap[row][col]

        legal_moves = []
        directions = []

        # Determine movement direction based on player
        if piece_id > 0:
            directions = [(1, 0),       # Black moves down
                          (1, -1),      # Black moves down-left
                          (1, 1)]       # Black moves down-right
        else:                           
            directions = [(-1, 0),      # White moves up
                          (-1, -1),     # White moves up-left
                          (-1, 1)]      # White moves up-right

        # Check for legal moves in each direction
        for dr, dc in directions:
            # Increment move in the direction
            row_i, col_i = row + dr, col + dc
            while self.Board.move_is_in_bounds(row_i, col_i):
                # Check if the square is empty or occupied
                if self.Board.square_is_empty(row_i, col_i):
                    legal_moves.append((row_i, col_i))
                else:
                    break
                row_i += dr
                col_i += dc
        return legal_moves

    # Purpose: Set cached legal moves
    def set_cached_legal_moves(self, piece_pos):
        self.cached_legal_moves = self.get_legal_moves(piece_pos)

    # Purpose: Check for game end condition when a player reaches the back rank
    def check_for_game_end_back_rank(self, row):
        # Check if the player has reached the back rank
        if (row == 0 and self.turn_player == self.WHITE_PLAYER) or \
           (row == self.Board.SETTINGS.DIM - 1 and self.turn_player == self.BLACK_PLAYER):
            return True
        return False
    
    # Purpose: Check for game end condition when a player causes a loop
    def check_for_game_end_loop(self, piece_id):
        # Check if both players have no legal moves
        if self.turn_skipped and len(self.cached_legal_moves) == 0:
            # Get color of the last moved piece
            row, col = self.Board.last_moved_piece_pos
            last_piece_id = self.Board.piece_bitmap[row][col]
            last_piece_color = self.Board.PIECE_ID_TO_COLOR[last_piece_id]
            last_piece_pos_color = self.Board.BOARD_COLORS[row][col]
            
            # Get color of current piece
            current_piece_color = self.Board.PIECE_ID_TO_COLOR[piece_id]
            current_piece_pos = self.Board.PIECE_ID_TO_POSITION[piece_id]
            current_piece_pos_color = self.Board.BOARD_COLORS[current_piece_pos[0]][current_piece_pos[1]]
            
            # Check for loop conditions:
            # 1) last moved piece color is the same as the current piece position color
            # 2) last moved piece position color is the same as the current piece color
            if (last_piece_color == current_piece_pos_color) and (last_piece_pos_color == current_piece_color):
                return True
        return False