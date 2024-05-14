import chess
from reconchess import utilities

def generate_next_moves(fen):
    board = chess.Board(fen)
    next_moves = []

    # Determine the color of the current side to move
    current_color = board.turn

    # Generate pseudo-legal moves for the current side to move
    for move in board.generate_legal_moves():
        # Check if the moved piece belongs to the current side
        if board.piece_at(move.from_square).color == current_color:
            next_moves.append(move)

    # Generate null move
    next_moves.append(chess.Move.null())

    # Generate castling moves for the current side to move
    for move in board.generate_castling_moves():
        if not utilities.is_illegal_castle(board, move):
            next_moves.append(move)

    # Sort moves alphabetically
    next_moves.sort(key=lambda move: str(move))

    return next_moves

# Read FEN string from input
fen = input()

# Generate next possible moves
moves = generate_next_moves(fen)

# Print moves
for move in moves:
    print(move)
