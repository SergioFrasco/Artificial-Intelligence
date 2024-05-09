import chess

def generate_next_positions(fen):
    board = chess.Board(fen)
    next_positions = []

    # Generate all legal moves for the current position
    legal_moves = list(board.legal_moves)

    # Apply each move to the board and generate the next position
    for move in legal_moves:
        board_copy = board.copy()
        board_copy.push(move)
        next_positions.append(board_copy)

    # Encode each resulting board position as a FEN string
    fen_strings = [position.fen() for position in next_positions]

    # Sort the list of FEN strings alphabetically
    fen_strings.sort()

    return fen_strings

# Read the FEN string from input
fen = input()

# Generate next possible positions
next_positions = generate_next_positions(fen)

# Print next possible positions
for fen_string in next_positions:
    print(fen_string)
