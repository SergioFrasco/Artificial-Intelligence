import chess


def execute_move(board, move):
    board = chess.Board(board)
    move = chess.Move.from_uci(move)
    board.push(move)
    return board.fen()

# Sample usage
board = input()
move = input()
print(execute_move(board, move))
