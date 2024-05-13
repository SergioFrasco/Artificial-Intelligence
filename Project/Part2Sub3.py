import chess
from reconchess import utilities

def generate_next_moves(fen):
    board = chess.Board(fen)
    next_moves = set()  # Use a set to prevent duplicate moves

    # Determine the color of the current side to move
    current_color = board.turn

    # Generate pseudo-legal moves for the current side to move
    for move in board.pseudo_legal_moves:
        # Check if the moved piece belongs to the current side
        if board.piece_at(move.from_square).color == current_color:
            next_moves.add(move)

    # Add null move
    next_moves.add(chess.Move.null())

    # Generate castling moves for the current side to move
    castling_moves = generate_castling_moves(board)
    next_moves.update(castling_moves)

    # Convert set back to a list and sort moves alphabetically
    sorted_moves = sorted(next_moves, key=lambda move: str(move))

    return sorted_moves

def generate_castling_moves(board):
    castling_moves = []
    for move in utilities.without_opponent_pieces(board).generate_castling_moves():
        if not utilities.is_illegal_castle(board, move):
            castling_moves.append(move)
    return castling_moves


def generate_next_positions(fen, capture_square):
    board = chess.Board(fen)
    next_positions = []

    # Determine the color of the current side to move
    current_color = board.turn

    # Generate legal moves for the current side to move
    for move in generate_next_moves(fen):
        # Apply the move to create a new board
        board.push(move)
        # Check if the move results in a capture on the specified square
        if board.is_capture(move) and chess.square_name(move.to_square) == capture_square:
            next_positions.append(board.fen())
        # Undo the move to explore other possibilities
        board.pop()

    # Sort positions alphabetically
    next_positions.sort()

    return next_positions


# Read FEN string from input
fen = input()
move = input()

# Generate next possible moves
moves = generate_next_positions(fen, move)

# Print moves
for move in moves:
    print(move)
