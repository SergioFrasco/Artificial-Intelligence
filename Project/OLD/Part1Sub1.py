import chess

def printBoard(x):
    board = chess.Board(x)
    print(board)

# Take in input and print the board
x = input()
printBoard(x)