import random
from reconchess import *
import os
import chess.engine
import numpy as np
import math

DEPTH = 1
TIME_LIMIT = 0.5

STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'

class ImprovedAgent(Player):
    def __init__(self):
        self.board = None
        self.color = None
        self.opponent_color = None
        self.took_king = False
        self.failed_move = []
        
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
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path, timeout=60)
        
    def handle_game_start(self, color: bool, board: chess.Board, opponent_name: str = None):
        self.board = board
        self.color = color
        self.possible_states = set()
        self.possible_states.add(self.board.fen())  # Add the initial board state to the set of possible states
        self.scholars_valid = True
        self.black_scholars_valid_left = False
        self.white_scholars_valid_left = False
        self.sensed_square = None

        # self.white_move = [chess.Move.from_uci("b1c3")]
        # self.white_move.append(chess.Move.from_uci("c3b5"))
        # self.white_move.append(chess.Move.from_uci("b5d6"))
        # self.white_move.append(chess.Move.from_uci("d6e8"))
        
        # self.black_move = [chess.Move.from_uci("b8c6")]
        # self.black_move.append(chess.Move.from_uci("c6b4"))
        # self.black_move.append(chess.Move.from_uci("b4d3"))
        # self.black_move.append(chess.Move.from_uci("d3e1"))

        self.black_move_right = [chess.Move.from_uci("e7e5")]
        self.black_move_right.append(chess.Move.from_uci("d8h4"))

        self.black_move_left = [chess.Move.from_uci("c7c5")]
        self.black_move_left.append(chess.Move.from_uci("d8a5"))
        
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
        if self.board.is_valid(): updated_states.add(self.board.fen())

        for state in self.possible_states:
            board = chess.Board(state)
            for move in board.pseudo_legal_moves: 
                if not captured_my_piece and move.to_square != capture_square:
                    if (len(updated_states) > 50000):
                        break

                    board.push(move)
                    updated_states.add(board.fen())
                    board.pop()
            
            if (len(updated_states) > 50000):
                break

        self.possible_states = updated_states
        print("Number of possible boards: ", len(self.possible_states))

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Square:
        if self.color == chess.WHITE:
            pass
        else:
            if self.move_number == 0:
                return chess.parse_square("e3")
            elif self.move_number == 1 and self.scholars_valid == True:
                if self.black_scholars_valid_left == True:
                    return chess.parse_square("c3")
                else:
                    return chess.parse_square("f3")

        # if our piece was just captured, sense where it was captured
        if self.my_piece_captured_square:
            return self.my_piece_captured_square

        # otherwise, just randomly choose a sense action, but don't sense on a square where our pieces are located
        # for square, piece in self.board.piece_map().items():
        #     if piece.color == self.color:
        #         sense_actions.remove(square)
        
        # Don't sense on a square along the edge
        edges = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 15, 16, 23, 24, 31, 32, 39, 40, 47, 48, 55, 56, 57, 58, 59, 60, 61, 62, 63])
        sense_actions = np.setdiff1d(sense_actions, edges)
        sense_actions = sense_actions.tolist()

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

        return random.choice(sense_actions)
        
    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        # add the pieces in the sense result to our board
        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)

        # if sholars is true and black_scholars_valid_left is true, do a left attack
        # if sholars is true and black_scholars_valid_left is false, do a right attack
        # if sholars is false, dont do any attack, just resort to stockfish
        
        # TO DO - WHITE SIDE
        
        if self.color == chess.BLACK:
            # Turn 0
            if self.move_number == 0:
                if self.board.piece_at(chess.parse_square("d2")) == None:
                    #EXECUTE LEFT SIDE ATTACK
                    self.black_scholars_valid_left = True
                    
                elif self.board.piece_at(chess.parse_square("f2")) == None:
                    #EXECUTE RIGHT SIDE ATTACK
                    self.black_scholars_valid_left = False
                    
                else:
                    self.scholars_valid = False

            # Turn 1
            elif self.move_number == 1:
                # if we sense the left side
                
                if self.sensed_square == chess.parse_square("c3"):
                    if not (self.board.piece_at("d2") == None and self.board.piece_at("c3") == None and self.board.piece_at("b4") == None):
                        self.scholars_valid = False
                
                # if we sensed the right side 
                elif self.sensed_square == chess.parse_square("f3"):
                    if not (self.board.piece_at("f2") == None and self.board.piece_at("g3") == None):
                        self.scholars_valid= False          
            

        # Remove all states that don't match the sense result
        consistent_states = set()
        consistent_states.add(self.board.fen())

        for state in self.possible_states:
            same = True
            board = chess.Board(state)

            for square, piece in sense_result:
                board_piece = board.piece_at(square)    

                if board_piece != piece:
                    same = False
                    break
            
            if same:
                consistent_states.add(state)
        
        self.possible_states = consistent_states

    def generate_move(self, board, move_actions, time_limit):    
        enemy_king_square = self.board.king(self.opponent_color)
        # print("Enemy king square is", enemy_king_square)
        if enemy_king_square != None:
            # if there are any ally pieces that can take king, execute one of those moves
            enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)
            if enemy_king_attackers:
                # print("Attacking enemy king")
                attacker_square = enemy_king_attackers.pop()
                #self.board.push(chess.Move(attacker_square, enemy_king_square))

                finishing_blow = chess.Move(attacker_square, enemy_king_square)
                if (finishing_blow in move_actions):
                    return finishing_blow
        
        # If no direct capture, ask Stockfish for a move
        try:
            # self.board.clear_stack()
            # print(board) 
            if(board.is_valid()):
                result = self.engine.play(board, chess.engine.Limit(depth=DEPTH, time=time_limit))
                # print(result.move)
                # print(move_actions)

                if result.move in move_actions:
                    # print("PICKED STOCKFISH BEST MOVE")
                    return result.move
            
            return random.choice(move_actions)
                
        except (chess.engine.EngineError, chess.engine.EngineTerminatedError) as e:
            print('Engine bad state at "{}"'.format(self.board.fen()))
        
        return None

    def most_common_move(self, moves):
        move_counts = {}
        for move in moves:
            if move in move_counts:
                move_counts[move] += 1
            else:
                move_counts[move] = 1
        
        max_count = max(move_counts.values())
        most_common_moves = [move for move, count in move_counts.items() if count == max_count]
        return most_common_moves[0]

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:

        # Limit the number of possible states to 10000
        if len(self.possible_states) > 10000:
            self.possible_states = random.sample(self.possible_states, 10000)

        self.board.turn = self.color

        time_limit = 10 / len(self.possible_states)

        self.move_number += 1

        if self.color == chess.WHITE:
            enemy_king_square = self.board.king(self.opponent_color)
            # print("Enemy king square is", enemy_king_square)
            if enemy_king_square != None:
                # if there are any ally pieces that can take king, execute one of those moves
                enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)
                if enemy_king_attackers:
                    # print("Attacking enemy king")
                    attacker_square = enemy_king_attackers.pop()
                    #self.board.push(chess.Move(attacker_square, enemy_king_square))
                    return chess.Move(attacker_square, enemy_king_square)
                
            if self.move_number < len(self.white_move):
                # print(self.move_number)
                self.move_number += 1
                # print(self.white_move[self.move_number - 1])
                #self.board.push(self.white_move[self.move_number - 1])
                if(self.white_move[self.move_number-1] in move_actions):
                    return self.white_move[self.move_number - 1]
                else:
                    self.move_number = 10
        else:

            # Execute the king if possible
            enemy_king_square = self.board.king(self.opponent_color)
            # print("Enemy king square is", enemy_king_square)
            if enemy_king_square != None:
                # if there are any ally pieces that can take king, execute one of those moves
                enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)
                if enemy_king_attackers:
                    # print("Attacking enemy king")
                    attacker_square = enemy_king_attackers.pop()
                    #self.board.push(chess.Move(attacker_square, enemy_king_square))
                    return chess.Move(attacker_square, enemy_king_square)
            
            # Turn 0 scholars mate
            if self.move_number-1 == 0 and self.scholars_valid:
                if self.color == chess.WHITE:
                    pass
                    # TO DO
                
                # if sholars is true and black_scholars_valid_left is true, do a left attack
                # if sholars is true and black_scholars_valid_left is false, do a right attack
                # if sholars is false, give up on scholars mate, just resort to stockfish
                else:
                    if self.black_scholars_valid_left:
                        if self.black_move_left[0] in move_actions:
                            return self.black_move_left[0]
                    else:
                        if self.black_move_right[0] in move_actions:
                            return self.black_move_right[0]

            # Turn 1 scholars mate    
            if self.move_number-1 == 1 and self.scholars_valid:
                if self.color == chess.WHITE:
                    pass
                    # TO DO
                
                # if sholars is true and we sensed the left side, do a left attack
                # if sholars is true and we sensed the right side, do a right attack
                # if sholars is false, give up on scholars mate, just resort to stockfish
                else:
                    if self.black_scholars_valid_left:
                        if self.black_move_left[1] in move_actions:
                            return self.black_move_left[1]
                    else:
                        if self.black_move_right[1] in move_actions:
                            return self.black_move_right[1]

            
    
        # generated_move = self.generate_move(self.board, move_actions, TIME_LIMIT)

        # Generate moves for each board
        generated_moves = [self.generate_move(chess.Board(state), move_actions, time_limit) for state in self.possible_states]

        most_common = self.most_common_move(generated_moves)

        print(self.board)

        return most_common

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move], captured_opponent_piece: bool, capture_square: Optional[Square]):
        
        # if self.move_number < len(self.white_move):
        #     if taken_move is None and requested_move is not None:
        #         self.move_number = 10

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