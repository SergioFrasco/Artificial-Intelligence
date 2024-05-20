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
    ImprovedAgent uses the Stockfish chess engine to choose moves. In order to run this agent you'll need to download
    Stockfish from https://stockfishchess.org/download/ and create an environment variable called STOCKFISH_EXECUTABLE
    that is the path to the downloaded Stockfish executable.
    """

    def __init__(self):
        self.board_states = set()
        self.color = None
        self.my_piece_captured_square = None
        self.move_number = 0

        # only play knight push when we're white
        self.white_move = [chess.Move.from_uci("b1c3")]
        self.white_move.append(chess.Move.from_uci("c3b5"))
        self.white_move.append(chess.Move.from_uci("b5d6"))
        self.white_move.append(chess.Move.from_uci("d6e8"))

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

        new_states = set()
        # if an opponent captured our piece, we should run through all the boards, make all possible moves where that move was possible and update the boards
        if captured_my_piece:
            for state in self.board_states:
                board = chess.Board(state)
                
                # find all possible moves where the capture was possible, only add those moves
                for move in board.pseudo_legal_moves:
                    if move.to_square == capture_square:
                        board.push(move)
                        new_states.add(board.fen())
                        board.pop()
        else:
            # otherwise, just copy the current set of possible boards
            new_states = self.board_states.copy()
        
        generated_states = set()
        # generate all possible moves for each state, this now becomes our new set of possible states
        for state in new_states: 
            board = chess.Board(state)
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

    def naive_entropy(self, sense_actions: List[Square]):
        set_of_board_objects = {state: chess.Board(state) for state in self.board_states}

        # determine entropy per square
        entropy_per_square = {}
        for square in range(64):
            count_per_piece = Counter(set_of_board_objects[state].piece_at(square) for state in self.board_states)
            total_count_on_square = sum(count_per_piece.values())

            entropy = -sum(count/total_count_on_square * math.log2(count/total_count_on_square) if count > 0 else 0 for count in count_per_piece.values())
            
            entropy_per_square[square] = entropy

        # determine entropy per 9x9 area
        entropy_per_region = {}
        for middle_square in sense_actions:
            area = [middle_square - 9, middle_square - 8, middle_square - 7,
                    middle_square - 1, middle_square, middle_square + 1,
                    middle_square + 7, middle_square + 8, middle_square + 9]
            
            entropy_per_region[middle_square] = sum(entropy_per_square[square] for square in area)

        uncertainty_minimizer = max(entropy_per_region, key=entropy_per_region.get)

        print(f"----ENTROPY Orginal Best Sense was: {chess.square_name(uncertainty_minimizer)}----")
        
        # padding around the edges in case we accidentally sense an edge somehow
        rank, file = divmod(uncertainty_minimizer, 8)
        if rank == 0:  # bottom border
            uncertainty_minimizer += 8  # move one square up
        elif rank == 7:  # top border
            uncertainty_minimizer -= 8  # move one square down
        elif file == 0:  # left border
            uncertainty_minimizer += 1  # move one square right
        elif file == 7:  # right border
            uncertainty_minimizer -= 1  # move one square left
        print(f"----ENTROPY Best sense after adjustments: {chess.square_name(uncertainty_minimizer)}----")   
        
        # return option that minimized uncertainty
        return uncertainty_minimizer

    def use_stockfish(self, sense_actions: List[Square]):
        # limit number of states if there are too many states to sense with
        if len(self.board_states) > 0: 
            if (len(self.board_states) > STATE_LIMIT):
                self.board_states = random.sample(self.board_states, STATE_LIMIT)

            time_limit = 10 / len(self.board_states) 

        # go through each possible board state
        ideal_senses = dict()
        for state in self.board_states:
            board = chess.Board(state)
            board.turn = not self.color
            board.clear_stack()
            if board.is_valid():
                
                try:
                    # determine stockfish's best move as the opponent
                    result = self.engine.play(board, chess.engine.Limit(time=time_limit))
                    
                    if result.move is not None:
                        if (result.move.to_square in sense_actions):
                            # count the moves across each board state
                            if result.move.to_square in ideal_senses.keys():
                                ideal_senses[result.move.to_square] += 1
                            else:
                                ideal_senses[result.move.to_square] = 1
                except (chess.engine.EngineError, chess.engine.EngineTerminatedError) as e:
                    pass

        if (len(ideal_senses.values()) == 0):
            print(f"STOCKFISH DIED, chose random")
            return random.choice(sense_actions)

        # get the most popular moves across each state, we break ties by just picking the first move in the list
        max_count = max(ideal_senses.values())
        best_senses = [move for move, count in ideal_senses.items() if count == max_count]

        # padding the sense result so we don't waste possible information gain
        if best_senses:

            print(f"----STOCKFISH Orginal Best Sense was: {chess.square_name(best_senses[0])}----")

            # adjust the sensing square if it is along the borders
            rank, file = divmod(best_senses[0], 8)
            if rank == 0:  # bottom border
                best_senses[0] += 8  # move one square up
            elif rank == 7:  # top border
                best_senses[0] -= 8  # move one square down
            elif file == 0:  # left border
                best_senses[0] += 1  # move one square right
            elif file == 7:  # right border
                best_senses[0] -= 1  # move one square left

            print(f"----STOCKFISH Best sense after adjustments: {chess.square_name(best_senses[0])}----")   

            return best_senses[0]

        print("It's choosing randomly in use_stockfish")
        return random.choice(sense_actions)

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> \
            Optional[Square]:
        print(f"In choose_sense {len(self.board_states)}")

        # always make these the first senses as stockfish is most likely to play these moves first
        if self.color == chess.WHITE:
            if self.move_number == 1:
                print("preset sense e6")
                return chess.parse_square("e6")
        else:
            if self.move_number == 0:
                print("preset sense e3")
                return chess.parse_square("e3")

        # if our piece was just captured, sense where it was captured
        if self.my_piece_captured_square:
            print("-----My piece was just captrured-----")
            return self.my_piece_captured_square

        # if the board state is perfectly known, use stockfish to sense the best square
        if len(self.board_states) == 1:
            return self.use_stockfish(sense_actions)
    
        # edges of the board being removed as possible senseing actions
        edges = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 15, 16, 23, 24, 31, 32, 39, 40, 47, 48, 55, 56, 57, 58, 59, 60, 61, 62, 63])
        sense_actions = np.setdiff1d(sense_actions, edges)
        sense_actions = sense_actions.tolist()

        # if there are multiple board states, use naive entropy to find the best sense to minimize
        # uncertainty about the board
        sense_square_using_naive_entropy = self.naive_entropy(sense_actions)

        return sense_square_using_naive_entropy

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        print(f"In handle_sense_result {len(self.board_states)}")

        # create a new set of board states based on the sense result
        new_board_states = set()

        # remove any board states that aren't consistent with what was seen in the window
        for state in self.board_states:
            board = chess.Board(state)
            flag = True
            for square, piece in sense_result:

                if board.piece_at(square) != piece:
                    flag = False
                    break

            if flag:
                new_board_states.add(board.fen())

        self.board_states = new_board_states

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        print(f"In choose_move {len(self.board_states)}")

        # if playing as white, execute the predefined rush moves
        if self.color == chess.WHITE and self.move_number < len(self.white_move):
            if self.white_move[self.move_number] in move_actions: #make sure the knight is still alive on the final move
                print("Attempting to kill king with move: ", self.move_number)
                return self.white_move[self.move_number]
        
        # limit the number of possible states if it is too high
        if len(self.board_states) > STATE_LIMIT:
            self.board_states = random.sample(self.board_states, STATE_LIMIT)

        # use the number of boards to set stockfish's time limit
        if len(self.board_states) > 0:
            time_limit = 10 / len(self.board_states)

        # if we run out of board states for some reason, just pick a random move
        else: 
            return random.choice(move_actions)
        
        # check if the king is under attack in any boards
        for state in self.board_states:
            board = chess.Board(state)
            king_square = board.king(self.color)
            if king_square:
                attackers = board.attackers(not self.color, king_square)
                if attackers:
                    # king is under attack, find the best move to avoid the attack
                    best_move = None
                    best_score = -float('inf')
                    for move in move_actions:
                        new_board = board.copy()
                        if move in new_board.pseudo_legal_moves:
                            new_board.push(move)
                            if not new_board.is_attacked_by(not self.color, king_square):
                                try:
                                    # use stockfish to find the best move to play such that we save the king
                                    result = self.engine.play(new_board, chess.engine.Limit(time=time_limit))
                                    score = result.info.get('score', None)
                                    if score is not None and score.white().score(mate_score=32000) > best_score:
                                        best_move = move
                                        best_score = score.white().score(mate_score=32000)
                                except (chess.engine.EngineTerminatedError, chess.engine.EngineError):
                                    pass
                    if best_move != None:
                        print("*Evasive maneuvre to get the king out of check*")
                        # whichever move across each possible state that yielded the best position for us after is returned
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
                        print("*Tried to kill the king*")
                        return chess.Move(attacker_square, enemy_king_square)

        # if we weren't under attack and couldn't kill the king
        move_counts = Counter()
        for state in self.board_states:
            board = chess.Board(state)
            board.turn = self.color
            try:
                # find stockfish's best move across each state
                result = self.engine.play(board, chess.engine.Limit(time=time_limit))
                if (result.move in move_actions):
                    move_counts[result.move] += 1
            except (chess.engine.EngineTerminatedError, chess.engine.EngineError):
                pass

        if move_counts:
            print("*Chose stockfish's most popular move*")
            # return the most popular move across all states
            return max(move_counts, key=move_counts.get)

        # if all else fails, just choose random
        return random.choice(move_actions)

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        print(f"In handle_move_result {len(self.board_states)}")
        
        self.move_number += 1

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