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

# Take input from console
fen_input = input()

# Generate and print output
move = generate_move(fen_input)
print(move)
