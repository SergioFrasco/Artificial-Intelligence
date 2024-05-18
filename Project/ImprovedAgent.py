import chess.engine
import random
from reconchess import *
import os
from collections import Counter
import math
from typing import List, Tuple, Optional
import chess
import numpy as np

STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'

STATE_LIMIT = 100000

class ImprovedAgent(Player):
    """
    TroutBot uses the Stockfish chess engine to choose moves. In order to run TroutBot you'll need to download
    Stockfish from https://stockfishchess.org/download/ and create an environment variable called STOCKFISH_EXECUTABLE
    that is the path to the downloaded Stockfish executable.
    """

    def __init__(self):
        self.board_states = set()
        self.color = None
        self.my_piece_captured_square = None

        # make sure stockfish environment variable exists
        if STOCKFISH_ENV_VAR not in os.environ:
            raise KeyError(
                'TroutBot requires an environment variable called "{}" pointing to the Stockfish executable'.format(
                    STOCKFISH_ENV_VAR))

        # make sure there is actually a file
        stockfish_path = os.environ[STOCKFISH_ENV_VAR]
        if not os.path.exists(stockfish_path):
            raise ValueError('No stockfish executable found at "{}"'.format(stockfish_path))

        # initialize the stockfish engine
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path, timeout=100)

    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.color = color
        self.board_states.add(board.fen())
        

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        print(f"In handle_opponent_move_result {len(self.board_states)}")
        
        self.my_piece_captured_square = capture_square

        # if the opponent captured our piece, remove it from all board states
        new_states = set()
        # if captured_my_piece:
        #     for state in self.board_states:
        #         board = chess.Board(state)
        #         board.remove_piece_at(capture_square)
        #         new_states.add(board.fen())
        #     self.board_states = new_states

        # instead if an opponent captured our piece, we should run through all the boards, make all possible moves where that move was possible and update the boards
        if captured_my_piece:
            for state in self.board_states:
                board = chess.Board(state)
                
                # Find all possible moves where the capture was possible
                for move in board.pseudo_legal_moves:
                    if move.to_square == capture_square:
                        board.push(move)
                        new_states.add(board.fen())
                        board.pop()
        else:
            new_states = self.board_states.copy()
        
        generated_states = set()
        for state in new_states:    #changed this from board states to new states so it takes into account the changes above if there were any
            board = chess.Board(state)
            # print(board)
            board.turn = not self.color
            for move in board.pseudo_legal_moves: 
                    if (len(generated_states) > STATE_LIMIT):
                        break
                    
                    board.push(move)
                    generated_states.add(board.fen())
                    board.pop()
            
            if (len(generated_states) > STATE_LIMIT):
                break
        
        self.board_states = generated_states
        # for state in generated_states:
        #     # print(chess.Board(state))
        #     self.board_states.add(state)

    def naive_entropy(self, sense_actions: List[Square]):
        """
        Implements the Naive Entropy sensing strategy.
        Calculates the entropy for each square on the board and selects the center square
        of the 3x3 region with the highest aggregate entropy.
        """
        # Cache board objects for each state
        board_cache = {state: chess.Board(state) for state in self.board_states}

        # Calculate entropy for each square
        square_entropies = {}
        for square in range(64):
            piece_counts = Counter(board_cache[state].piece_at(square) for state in self.board_states)
            total = sum(piece_counts.values())
            entropy = -sum(count/total * math.log2(count/total) if count > 0 else 0 for count in piece_counts.values())
            square_entropies[square] = entropy

        # Compute aggregate entropy for each 3x3 region
        region_entropies = {}
        for center_square in sense_actions:
            region = [center_square - 9, center_square - 8, center_square - 7,
                    center_square - 1, center_square, center_square + 1,
                    center_square + 7, center_square + 8, center_square + 9]
            region_entropy = sum(square_entropies[square] for square in region)
            
            region_entropies[center_square] = region_entropy 

        best_square = max(region_entropies, key=region_entropies.get)

        print(f"----ENTROPY Orginal Best Sense was: {chess.square_name(best_square)}----")
            # Adjust the sensing square if it is along the borders
        rank, file = divmod(best_square, 8)
        if rank == 0:  # Bottom border
            best_square += 8  # Move one square up
        elif rank == 7:  # Top border
            best_square -= 8  # Move one square down
        elif file == 0:  # Left border
            best_square += 1  # Move one square right
        elif file == 7:  # Right border
            best_square -= 1  # Move one square left
        print(f"----ENTROPY Best sense after adjustments: {chess.square_name(best_square)}----")   
        
        return best_square

    def use_stockfish(self, sense_actions: List[Square]):
        if len(self.board_states) > 0: 
            if (len(self.board_states) > STATE_LIMIT):
                self.board_states = random.sample(self.board_states, STATE_LIMIT)

            time_limit = 10 / len(self.board_states) 
        # else:
        #     # print("Sensed the centre")
        #     central_squares = [
        #         chess.D4, chess.E4, chess.D5, chess.E5,
        #         chess.C4, chess.F4, chess.C5, chess.F5,
        #         chess.C3, chess.D3, chess.E3, chess.F3,
        #         chess.C6, chess.D6, chess.E6, chess.F6
        #     ]
        #     for square in central_squares:
        #         if square in sense_actions:
        #             return square

        ideal_senses = dict()
        for state in self.board_states:
            board = chess.Board(state)
            board.turn = not self.color
            board.clear_stack()
            if board.is_valid():
                
                try:
                    result = self.engine.play(board, chess.engine.Limit(time=time_limit))
                    
                    if result.move is not None:
                        if (result.move.to_square in sense_actions):
                            if result.move.to_square in ideal_senses.keys():
                                ideal_senses[result.move.to_square] += 1
                            else:
                                ideal_senses[result.move.to_square] = 1
                except (chess.engine.EngineError, chess.engine.EngineTerminatedError) as e:
                    # print('Engine bad state at "{}"'.format(board.fen()))
                    # print(board)
                    pass
                # print(result.move.to_square) 
        # print(len(self.board_states))

        if (len(ideal_senses.values()) == 0):
            print(f"STOCKFISH DIED, chose random")
            return random.choice(sense_actions)

        max_count = max(ideal_senses.values())
        best_senses = [move for move, count in ideal_senses.items() if count == max_count]

        if best_senses:
            # print(f"Number of moves: {len(best_senses)}")
            print(f"----STOCKFISH Orginal Best Sense was: {chess.square_name(best_senses[0])}----")
            # Adjust the sensing square if it is along the borders
            rank, file = divmod(best_senses[0], 8)
            if rank == 0:  # Bottom border
                best_senses[0] += 8  # Move one square up
            elif rank == 7:  # Top border
                best_senses[0] -= 8  # Move one square down
            elif file == 0:  # Left border
                best_senses[0] += 1  # Move one square right
            elif file == 7:  # Right border
                best_senses[0] -= 1  # Move one square left
            print(f"----STOCKFISH Best sense after adjustments: {chess.square_name(best_senses[0])}----")   

            return best_senses[0]

        
        return random.choice(sense_actions)

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> \
            Optional[Square]:
        print(f"In choose_sense {len(self.board_states)}")

        # if our piece was just captured, sense where it was captured
        if self.my_piece_captured_square:
            return self.my_piece_captured_square

        # if we might capture a piece when we move, sense where the capture will occur
        # future_move = self.choose_move(move_actions, seconds_left)
        # if future_move is not None and any(chess.Board(board).piece_at(future_move.to_square) is not None for board in self.board_states):
        #     return future_move.to_square

        if len(self.board_states) == 1:
            return self.use_stockfish(sense_actions)

        edges = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 15, 16, 23, 24, 31, 32, 39, 40, 47, 48, 55, 56, 57, 58, 59, 60, 61, 62, 63])
        sense_actions = np.setdiff1d(sense_actions, edges)
        sense_actions = sense_actions.tolist()

        sense_square_using_naive_entropy = self.naive_entropy(sense_actions)

        return sense_square_using_naive_entropy

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        print(f"In handle_sense_result {len(self.board_states)}")

        # create a new set of board states based on the sense result
        new_board_states = set()

        for state in self.board_states:
            board = chess.Board(state)
            flag = True
            for square, piece in sense_result:
                # print(board.piece_at(square), piece) 
                if board.piece_at(square) != piece:
                    flag = False
                    break

            if flag:
                # print("BOARD WAS VALIDDDD")
                # print(board)
                new_board_states.add(board.fen())

        self.board_states = new_board_states

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        print(f"In choose_move {len(self.board_states)}")

        # Limit the number of possible states
        if len(self.board_states) > STATE_LIMIT:
            self.board_states = random.sample(self.board_states, STATE_LIMIT)

        if len(self.board_states) > 0:
            time_limit = 10 / len(self.board_states)
        else:
            return random.choice(move_actions)
        
        # Check if the king is under attack
        for state in self.board_states:
            board = chess.Board(state)
            king_square = board.king(self.color)
            if king_square:
                attackers = board.attackers(not self.color, king_square)
                if attackers:
                    # King is under attack, find the best move to avoid the attack
                    best_move = None
                    best_score = -float('inf')
                    for move in move_actions:
                        new_board = board.copy()
                        if move in new_board.pseudo_legal_moves:
                            new_board.push(move)
                            if not new_board.is_attacked_by(not self.color, king_square):
                                try:
                                    result = self.engine.play(new_board, chess.engine.Limit(time=time_limit))
                                    score = result.info.get('score', None)
                                    if score is not None and score.white().score(mate_score=32000) > best_score:
                                        best_move = move
                                        best_score = score.white().score(mate_score=32000)
                                except (chess.engine.EngineTerminatedError, chess.engine.EngineError):
                                    pass
                    if best_move != None:
                        return best_move

        # if we might be able to take the king, try to
        for state in self.board_states:
            board = chess.Board(state)
            enemy_king_square = board.king(not self.color)
            if enemy_king_square:
                # if there are any ally pieces that can take king, execute one of those moves
                enemy_king_attackers = board.attackers(self.color, enemy_king_square)
                if enemy_king_attackers:
                    attacker_square = enemy_king_attackers.pop()
                    if chess.Move(attacker_square, enemy_king_square) in move_actions:
                        return chess.Move(attacker_square, enemy_king_square)

        # get the most popular move among all board states
        move_counts = Counter()
        for state in self.board_states:
            board = chess.Board(state)
            board.turn = self.color
            try:
                result = self.engine.play(board, chess.engine.Limit(time=time_limit))
                if (result.move in move_actions):
                    move_counts[result.move] += 1
            except (chess.engine.EngineTerminatedError, chess.engine.EngineError):
                pass

        if move_counts:
            return max(move_counts, key=move_counts.get)

        # if all else fails, pass
        return random.choice(move_actions)

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        print(f"In handle_move_result {len(self.board_states)}")
        
        new_states = set()
        # if a move was executed, apply it to all board states
        if taken_move is not None:
            # if the move we chose worked, update all boards with this move
            for state in self.board_states:
                board = chess.Board(state)

                if taken_move in board.pseudo_legal_moves:
                    if captured_opponent_piece:
                        if (board.piece_at(capture_square) == captured_opponent_piece):
                            board.remove_piece_at(capture_square)

                    if taken_move in board.pseudo_legal_moves:
                        board.push(taken_move)
                        if board.is_valid(): new_states.add(board.fen())
                else:
                    # if the taken move wasn't possible, exclude this board
                    pass
        else:
            # if we tried to take, but failed because something was in the way
            if requested_move is not None:
                # exclude all boards where the move was possible
                for state in self.board_states:
                    board = chess.Board(state)
                    if (requested_move not in board.pseudo_legal_moves):
                        new_states.add(board.fen())
        
        self.board_states = new_states

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        try:
            # if the engine is already terminated then this call will throw an exception
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass