import chess
import chess.engine

def generate_move(fen):
    board = chess.Board(fen)
    
    # Check if our piece can capture the opposing king
    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            if board.is_checkmate():
                return move.uci()
            board.pop()
    
    # If no direct capture, ask Stockfish for a move
    with chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True) as engine:
        result = engine.play(board, chess.engine.Limit(time=0.5))
        return result.move.uci()

def most_common_move(moves):
    move_counts = {}
    for move in moves:
        if move in move_counts:
            move_counts[move] += 1
        else:
            move_counts[move] = 1
    
    max_count = max(move_counts.values())
    most_common_moves = [move for move, count in move_counts.items() if count == max_count]
    return sorted(most_common_moves)[0]

# Take input from console
N = int(input())
fen_inputs = [input() for _ in range(N)]

# Generate moves for each board
moves = [generate_move(fen) for fen in fen_inputs]

# Find the most common move
most_common = most_common_move(moves)

# Print the most common move
print(most_common)
