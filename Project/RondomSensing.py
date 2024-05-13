# Sergio Frasco (2427724)
# Tristan Dos Remendos ()

import chess
import chess.engine
from reconchess import utilities
from stockfish import Stockfish
import random

class RondomSensing(Player):
    # Initialise the board and its attributes
    def __init__(self):
        self.board = None
        self.color = None
        self.opponent_name = None
        self.my_piece_captured_square = None
        self.possible_states = set()
        self.stockfish = Stockfish(path="C:\Users\Sergio\Documents\GitHub\Artificial-Intelligence\Project\stockfish-windows-x86-64-avx2\stockfish\stockfish.exe")
        self.stockfish.set_depth(12)  # Adjust depth

    # Implement other methods...
    def handle_game_start(self, color, board, opponent_name):
        self.color = color
        self.board = board
        self.opponent_name = opponent_name
        self.possible_states = set()
        self.my_piece_captured_square = None
        self.possible_states.add(self.board.fen())  # Add the initial board state to the set of possible states

        # Print the game information
        print(f"Game started. Playing as {self.color} against {self.opponent_name}")
        print(f"Initial board state: {self.board.fen()}")

    # handle the result of the opponents move
    def handle_opponent_move_result(self, captured_my_piece, capture_square):
        if captured_my_piece:
            self.my_piece_captured_square = capture_square
            print(f"Opponent captured my piece on square {chess.square_name(capture_square)}")
        else:
            self.my_piece_captured_square = None
            print("Opponent did not capture any of my pieces")

        # Update the set of possible states based on the opponent's move
        updated_states = set()
        for state in self.possible_states:
            board = chess.Board(state)
            for move in board.legal_moves:
                if captured_my_piece and chess.square_name(capture_square) == chess.square_name(move.to_square):
                    board.push(move)
                    updated_states.add(board.fen())
                    board.pop()
                elif not captured_my_piece and move.to_square != capture_square:
                    board.push(move)
                    updated_states.add(board.fen())
                    board.pop()
        self.possible_states = updated_states

    # implement the logic for selecting a sensing move.
    def choose_sense(self, sense_actions, move_actions, seconds_left):
         # Filter out squares on the edges of the board
        valid_squares = [square for square in chess.SQUARES if 1 <= chess.square_rank(square) <= 6 and 1 <= chess.square_file(square) <= 6]
        chosen_square = random.choice(valid_squares)
        return chosen_square# Randomly select a square from the valid squares
    
    # Update State of the squares within the sensing window.
    def handle_sense_result(self, sense_result):
        # Print the sensing result for debugging or logging purposes
        print(f"Sensing result: {sense_result}")

        # Update the set of possible states based on the sensing result
        updated_states = set()
        for state in self.possible_states:
            board = chess.Board(state)
            is_consistent = True
            for square, piece in sense_result.items():
                if board.piece_at(chess.parse_square(square)) != piece:
                    is_consistent = False
                    break
            if is_consistent:
                updated_states.add(state)
        self.possible_states = updated_states

    # Get stockfish to choose a move for us
    def choose_move(self, move_actions, seconds_left):
        # Limit the number of possible states to 10000
        if len(self.possible_states) > 10000:
            self.possible_states = random.sample(self.possible_states, 10000)

        time_limit = 10 / len(self.possible_states) # Set the time limit based on the number of possible states
        move_counts = {}  # Initialize a dictionary to store the move counts

        # Iterate over each possible state
        for state in self.possible_states:
            board = chess.Board(state)

            # Set the position on the Stockfish board
            self.stockfish.set_fen_position(state)

            # Get the best move from Stockfish with the time limit
            best_move = self.stockfish.get_best_move_time(time_limit * 1000)

            # Increment the count for the best move
            if best_move in move_counts:
                move_counts[best_move] += 1
            else:
                move_counts[best_move] = 1

        # Find the move with the highest count
        majority_move = max(move_counts, key=move_counts.get)

        # Print the chosen move
        print(f"Chosen move: {majority_move}")

        return majority_move

    # Update the board based on the result of our move
    def handle_move_result(self, requested_move, taken_move, captured_opponent_piece, capture_square):
        # Print the move result 
        print(f"Requested move: {requested_move}")
        print(f"Taken move: {taken_move}")
        print(f"Captured opponent piece: {captured_opponent_piece}")
        print(f"Capture square: {capture_square}")

        # Update the set of possible states based on the move result
        updated_states = set()
        for state in self.possible_states:
            board = chess.Board(state)
            if board.is_legal(taken_move):
                board.push(taken_move)
                updated_states.add(board.fen())
        self.possible_states = updated_states

        # Update the board state with the taken move
        self.board.push(taken_move)

    # Close out of stockfish and the agent
    def handle_game_end(self, winner_color, win_reason, game_history):
        # Print the game result for debugging or logging purposes
        print(f"Game ended. Winner: {winner_color}, Reason: {win_reason}")

        # Close the Stockfish engine
        self.stockfish.quit()

        # Exit the agent
        exit()
