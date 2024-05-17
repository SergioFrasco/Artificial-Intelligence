import random
from reconchess import *
import os
import chess.engine
import math

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
        self.possible_states = set()
        self.possible_states.add(self.board.fen())  # Add the initial board state to the set of possible states
        
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

            # Remove all states that assume the captured piece wasn't taken
            updated_states = set()
            updated_states.add(self.board.fen())

            for state in self.possible_states:
                board = chess.Board(state)
                if board.piece_at(capture_square) is None:
                    updated_states.add(state)

            self.possible_states = updated_states    

        # Update the set of possible states based on the opponent's move
        updated_states = set()
        updated_states.add(self.board.fen())

        for state in self.possible_states:
            board = chess.Board(state)
            for move in board.pseudo_legal_moves: 
                if not captured_my_piece and move.to_square != capture_square:
                    if (len(updated_states) > 10000):
                        break

                    board.push(move)
                    updated_states.add(board.fen())
                    board.pop()
            
            if (len(updated_states) > 10000):
                break

        self.possible_states = updated_states
        print("Number of possible boards: ", len(self.possible_states))

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Square:
        # otherwise, calculate the entropy for each sense action and choose the one with the highest entropy
        entropy_scores = {}
        for square in sense_actions:
            piece_counts = {}
            for state in self.possible_states:
                board = chess.Board(state)
                piece = board.piece_at(square)
                if piece is None:
                    piece_type = '?'
                else:
                    piece_type = piece.symbol()
                piece_counts[piece_type] = piece_counts.get(piece_type, 0) + 1

            total_states = len(self.possible_states)
            entropy = 0
            for count in piece_counts.values():
                probability = count / total_states
                entropy -= probability * math.log2(probability)

            entropy_scores[square] = entropy

        max_entropy_square = max(entropy_scores, key=entropy_scores.get)
        return max_entropy_square

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

        time_limit = 10 / len(self.possible_states) # Set the time limit based on the number of possible states
        move_counts = {}  # Initialize a dictionary to store the move counts

        for state in self.possible_states:

            try:
                self.board.turn = self.color
                board = chess.Board(state) # Convert a fen string to a chess board before evaluating it

                # self.board.clear_stack()
                # print(self.board) 
                if(self.board.is_valid()):
                    result = self.engine.play(board, chess.engine.Limit(depth=DEPTH, time=time_limit))
                    # print(result.move)
                    # print(move_actions)

                    if result.move in move_actions:
                        # print("PICKED STOCKFISH BEST MOVE")
                        # return result.move
                        if result.move in move_counts.keys():
                            move_counts[result.move] += 1
                        else:
                            move_counts[result.move] = 1
                    
            except (chess.engine.EngineError, chess.engine.EngineTerminatedError) as e:
                print('Engine bad state at "{}"'.format(self.board.fen()))   

        if len(move_counts.keys()) != 0: 
            max_count = max(move_counts.values())
            most_common_moves = [move for move, count in move_counts.items() if count == max_count]
            move = sorted(most_common_moves)[0]

            print("=========USING MOST COMMON STOCKFISH MOVE==========\n the move is: ", move)
            return move

        # def intersection(lst1, lst2): return [value for value in lst1 if value in lst2]

        # next_moves = list()
        # # Generate pseudo-legal moves for the current side to move
        # for move in self.board.pseudo_legal_moves:
        #     # Check if the moved piece belongs to the current side
        #     if self.board.piece_at(move.from_square).color == self.color:
        #         next_moves.append(move) 

        return random.choice(move_actions + [None])

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move], captured_opponent_piece: bool, capture_square: Optional[Square]):
        
        if taken_move is not None:
            # print("In handle move result")
            # self.board.push(chess.Move.null())
            if taken_move in self.board.pseudo_legal_moves:
                self.board.push(taken_move)

            changed_states = set()
            for state in self.possible_states:
                board = chess.Board(state)

                if taken_move in board.pseudo_legal_moves:
                    changed_states.add(board.fen())

            changed_states.add(self.board.fen())
            self.possible_states = changed_states

            # else:
            #     print(f"Attempted to push an illegal move: {taken_move}")
        else:
            if requested_move is not None:

                changed_states = set()
                for state in self.possible_states:
                    board = chess.Board(state)

                    if requested_move not in board.pseudo_legal_moves:
                        changed_states.add(board.fen())
                
                self.possible_states = changed_states

                # else:
                #     print(f"Attempted to push an illegal move: {requested_move}")

            print(f"Failed to take using move: {requested_move}")

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason], game_history: GameHistory):
        
        print("We are WHITE") if self.color == chess.WHITE else print("We are BLACK") 

        self.engine.quit()