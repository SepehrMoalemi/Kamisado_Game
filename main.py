# Purpose: Driver File
# %------------------------------------------ Packages ------------------------------------% #
import board, game    
# %-------------------------------------------- Main  ------------------------------------% #
def main():
    # Set GUI Settings
    DIM       = 8                                  # Board of (DIM X DIM)
    LENGTH    = 512                                # Height and Width of the Board
    CELL_SIZE = LENGTH//DIM       
    MAX_FPS   = 60
    
    # Set Board Settings
    BOARD_COLOR_OPTIONS  = ["default", "rotate 90", "rotate 180", "rotate 270"]
    BOARD_STARTING_COLOR = BOARD_COLOR_OPTIONS[0]  # Default Board Color is default   
    BOARD_PIECE_SHAPE    = "rooks"                 # Default Piece Shape is simple_circle
    SETTINGS  = board.Settings(DIM=DIM,
                               LENGTH=LENGTH,
                               CELL_SIZE=CELL_SIZE,
                               MAX_FPS=MAX_FPS,
                               BOARD_STARTING_COLOR=BOARD_STARTING_COLOR,
                               BOARD_PIECE_SHAPE=BOARD_PIECE_SHAPE)
    # Run Game
    Kamisado = game.Kamisado(SETTINGS)
    Kamisado.run()
# %--------------------------------------------- Run -------------------------------------% #
if __name__ == '__main__':
    print(f'{"Start":-^{50}}')
    main()
    print(f'{"End":-^{50}}')