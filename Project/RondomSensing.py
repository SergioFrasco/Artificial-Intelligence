class RondomSensing(Player):
    def __init__(self):
    # setup agent as you see fit
        pass
    def handle_game_start(self, color, board, opponent_name):
    # function that is run when the game starts
        pass
    def handle_opponent_move_result(self, captured_my_piece, capture_square):
    # feedback on whether the opponent captured a piece
        pass
    def choose_sense(self, sense_actions, move_actions, seconds_left):
    # write code here to select a sensing move
        pass
    def handle_sense_result(self, sense_result):
    # This is where the sensing result returns feedback
        pass
    def choose_move(self, move_actions, seconds_left):
    # execute a chess move
        pass
    def handle_move_result(self, requested_move, taken_move, captured_opponent_piece, capture_square):
    # this function is called after your move is executed.
        pass
    def handle_game_end(self, winner_color, win_reason, game_history):

    # shut down everything at the end of the ga,e
        pass
