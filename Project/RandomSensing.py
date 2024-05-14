import random
from reconchess import *
import os
import chess.engine

DEPTH = 1
TIME_LIMIT = 0.5

STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'

class RandomSensingAgent(Player):
    def __init__(self):
        self.board = None
        self.color = None
        self.opponent_color = None
        self.took_king = False
        
        self.my_piece_captured_square = None
        self.move_number = 0
        
        # check if stockfish environment variable exists
        if STOCKFISH_ENV_VAR not in os.environ:
            raise KeyError(
                'Require an environment variable called "{}" pointing to the Stockfish executable'.format(
                    STOCKFISH_ENV_VAR))

        # make sure there is actually a file
        stockfish_path = os.environ[STOCKFISH_ENV_VAR]
        if not os.path.exists(stockfish_path):
            raise ValueError('No stockfish executable found at "{}"'.format(stockfish_path))

        # initialize the stockfish engine
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path, timeout=30)
        
    def handle_game_start(self, color: bool, board: chess.Board, opponent_name: str = None):
        self.board = board
        self.color = color
        
        if self.color == chess.WHITE:
            print("We are WHITE")
            self.opponent_color = chess.BLACK
        else:
            print("We are BLACK")
            self.opponent_color = chess.WHITE
        
    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        # if the opponent captured our piece, remove it from our board.
        self.my_piece_captured_square = capture_square
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Square:
        # otherwise, random sense action
        for square, piece in self.board.piece_map().items():
            if piece.color == self.color:
                sense_actions.remove(square)

        return random.choice(sense_actions)

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        # add changes to board, if any
        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        enemy_king_square = self.board.king(self.opponent_color)
        # print("Enemy king square is", enemy_king_square)
        if enemy_king_square != None:
            # if there are any ally pieces that can take king, execute one of those moves
            enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)
            if enemy_king_attackers:
                print("Attacking enemy king")
                attacker_square = enemy_king_attackers.pop()
                #self.board.push(chess.Move(attacker_square, enemy_king_square))

                finishing_blow = chess.Move(attacker_square, enemy_king_square)
                if (finishing_blow in move_actions):
                    return finishing_blow

        try:
            self.board.turn = self.color
            # self.board.clear_stack()
            print(self.board) 
            if(self.board.is_valid()):
                result = self.engine.play(self.board, chess.engine.Limit(depth=DEPTH, time=TIME_LIMIT))
                print(result.move)
                # print(move_actions)

                if result.move in move_actions:
                    print("PICKED STOCKFISH BEST MOVE")
                    return result.move
                
            def intersection(lst1, lst2): return [value for value in lst1 if value in lst2]

            next_moves = list()
            # Generate pseudo-legal moves for the current side to move
            for move in self.board.pseudo_legal_moves:
                # Check if the moved piece belongs to the current side
                if self.board.piece_at(move.from_square).color == self.color:
                    next_moves.append(move)
            
            return random.choice(intersection(move_actions, next_moves) + [None])
                
        except (chess.engine.EngineError, chess.engine.EngineTerminatedError) as e:
            print('Engine bad state at "{}"'.format(self.board.fen()))   

        def intersection(lst1, lst2): return [value for value in lst1 if value in lst2]

        next_moves = list()
        # Generate pseudo-legal moves for the current side to move
        for move in self.board.pseudo_legal_moves:
            # Check if the moved piece belongs to the current side
            if self.board.piece_at(move.from_square).color == self.color:
                next_moves.append(move) 

        return random.choice(intersection(move_actions, next_moves) + [None])

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move], captured_opponent_piece: bool, capture_square: Optional[Square]):
        
        if taken_move is not None:
            # print("In handle move result")
            # self.board.push(chess.Move.null())
            if taken_move in self.board.pseudo_legal_moves:
                self.board.push(taken_move)
            else:
                print(f"Attempted to push an illegal move: {taken_move}")
        else:
            # if requested_move is not None:
            #     # self.board.push(chess.Move.null())
            #     if requested_move in self.board.pseudo_legal_moves:
            #         self.board.push(requested_move)
            #     else:
            #         print(f"Attempted to push an illegal move: {requested_move}")

            print(f"Failed to take using move: {requested_move}")

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason], game_history: GameHistory):
        
        print("We are WHITE") if self.color == chess.WHITE else print("We are BLACK") 

        self.engine.quit()