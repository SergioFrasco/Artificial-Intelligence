# Sergio Frasco (2427724)
# Tristan Dos Remendos (2465830)

import chess
import chess.engine
from reconchess import *
from stockfish import Stockfish
import random
import os

STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'

class RandomSensing(Player):
    # Initialise the board and its attributes
    def __init__(self):
        self.board = None
        self.color = None
        self.opponent_name = None
        self.my_piece_captured_square = None
        self.possible_states = set()

        # make sure stockfish environment variable exists
        if STOCKFISH_ENV_VAR not in os.environ:
            raise KeyError(
                'TroutBot requires an environment variable called "{}" pointing to the Stockfish executable'.format(
                    STOCKFISH_ENV_VAR))

        # make sure there is actually a file
        stockfish_path = os.environ[STOCKFISH_ENV_VAR]
        if not os.path.exists(stockfish_path):
            raise ValueError('No stockfish executable found at "{}"'.format(stockfish_path))
        
        self.stockfish = Stockfish(path=stockfish_path)
        self.stockfish.set_depth(1)  # Adjust depth

        # initialize the stockfish engine
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

    # Initialise the start of the game
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
            for s in sense_result:
                square, piece = s
                if board.piece_at(square) != piece:
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

        if len(self.possible_states) == 0:
            print("+++++ PICKING RANDOM MOVE LOL +++++")

            def intersection(lst1, lst2): return [value for value in lst1 if value in lst2]

            next_moves = list()
            # Generate pseudo-legal moves for the current side to move
            for move in self.board.pseudo_legal_moves:
                # Check if the moved piece belongs to the current side
                if self.board.piece_at(move.from_square).color == self.color:
                    next_moves.append(move)
            
            return random.choice(intersection(move_actions, next_moves))
        
        time_limit = 10 / len(self.possible_states) # Set the time limit based on the number of possible states
        move_counts = {}  # Initialize a dictionary to store the move counts

        # Iterate over each possible state
        for state in self.possible_states:
            board = chess.Board(state)

            # Set the position on the Stockfish board
            self.stockfish.set_fen_position(state)

            # Get the best move from Stockfish with the time limit
            best_move = self.stockfish.get_best_move_time(time=0.5)

            # Increment the count for the best move
            if best_move in move_counts:
                move_counts[best_move] += 1
            else:
                move_counts[best_move] = 1

        # Find the move with the highest count
        majority_move_str = max(move_counts, key=move_counts.get)

        # Convert the majority move string to a chess.Move object
        majority_move = chess.Move.from_uci(majority_move_str)

        # Verify move validity
        board = chess.Board(list(self.possible_states)[0])  # Get the board position from the first possible state
         # Check if the majority move is a legal move
        if majority_move in move_actions:
            # Print the chosen move
            print(f"Chosen move: {majority_move}")
            return majority_move
        else:
            # If the majority move is not legal, choose a random legal move
            legal_moves = list(move_actions)
            if legal_moves:
                random_move = random.choice(legal_moves)
                print(f"Chosen move (random): {random_move}")
                return random_move
            else:
                # If there are no legal moves, return None
                print("No legal moves available.")
                return None
        
        
        # if majority_move in board.legal_moves:
        #     # Print the chosen move
        #     print(f"Chosen move: {majority_move}")
        #     return majority_move
        # else:
        #     # Handle invalid move (e.g., select another move)
        #     print("Chosen move is not valid. Selecting another move.")
        #     # Example: return the first legal move as a fallback
        #     return next(iter(board.legal_moves), None)


    # Update the board based on the result of our move
    def handle_move_result(self, requested_move, taken_move, captured_opponent_piece, capture_square):
        # Print the move result 
        print(f"Requested move: {requested_move}")
        print(f"Taken move: {taken_move}")
        print(f"Captured opponent piece: {captured_opponent_piece}")
        print(f"Capture square: {capture_square}")

        if taken_move is None:
            # The requested move was invalid, and the turn is forfeited
            print("Invalid move. Turn forfeited.")
            return

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
        if winner_color == False:
            print(f"pip pip! We won my fellow gentlemen due to {win_reason}")
        else:
            print(f"WE LOST FUUUUUUU Because of bullshit: {win_reason}")

        # Close the Stockfish engine
        self.engine.quit()

        # Exit the agent
        # exit()
