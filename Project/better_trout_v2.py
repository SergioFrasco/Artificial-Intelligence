import chess.engine
import random
from reconchess import *
import os
from collections import defaultdict
import math

STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'

class TroutBot(Player):
    """
    TroutBot uses the Stockfish chess engine to choose moves. In order to run TroutBot you'll need to download
    Stockfish from https://stockfishchess.org/download/ and create an environment variable called STOCKFISH_EXECUTABLE
    that is the path to the downloaded Stockfish executable.
    """

    def __init__(self):
        self.board = None
        self.color = None
        self.my_piece_captured_square = None
        self.states = set()

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
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path, setpgrp=True, timeout=30)

    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.board = board
        self.color = color

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):

        print(len(self.states))
        # if the opponent captured our piece, remove it from our board.
        self.my_piece_captured_square = capture_square
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> \
            Optional[Square]:
        # if our piece was just captured, sense where it was captured
        if self.my_piece_captured_square:
            return self.my_piece_captured_square

        # Calculate entropy for each square in a 3x3 area
        max_entropy = float('-inf')
        best_square = None

        for square in sense_actions:
            entropy = self.calculate_entropy(square)
            if entropy > max_entropy:
                max_entropy = entropy
                best_square = square

        return best_square

    def calculate_entropy(self, square: Square) -> float:
        # Calculate entropy for a given square
        piece_counts = defaultdict(int)
        total_states = len(self.states)

        for state in self.states:
            if piece is not None:
                piece = state.piece_at(square)
                piece_counts[piece] += 1

        entropy = 0.0
        for count in piece_counts.values():
            probability = count / total_states
            entropy -= probability * math.log2(probability)

        return entropy

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        # Add the sensed board state to the set of states
        self.states.add(chess.Board().set_piece_map(dict(sense_result)))

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        # If we might be able to take the king, try to
        enemy_king_square = self.board.king(not self.color)
        if enemy_king_square:
            # If there are any ally pieces that can take king, execute one of those moves
            enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)
            if enemy_king_attackers:
                attacker_square = enemy_king_attackers.pop()
                return chess.Move(attacker_square, enemy_king_square)

        # Otherwise, try to move with the Stockfish chess engine
        try:
            self.board.turn = self.color
            self.board.clear_stack()
            result = self.engine.play(self.board, chess.engine.Limit(depth=1, time=0.5))
            return result.move
        except chess.engine.EngineTerminatedError:
            print('Stockfish Engine died')
        except chess.engine.EngineError:
            print('Stockfish Engine bad state at "{}"'.format(self.board.fen()))

        # If all else fails, pass
        return None

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        # If a move was executed, apply it to our board and clear the set of states
        if taken_move is not None:
            self.board.push(taken_move)
            self.states.clear()

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        try:
            # If the engine is already terminated then this call will throw an exception
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass
