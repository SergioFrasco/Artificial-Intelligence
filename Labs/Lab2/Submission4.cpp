#include <iostream>
#include <vector>

using namespace std;

void printBoard(const vector<vector<char>>& board) {
    for (size_t i = 0; i < board.size(); ++i) {
        for (size_t j = 0; j < board[i].size(); ++j) {
            if(board[i][j] == '.'){
                cout << "_";
            }
            else{
                cout << board[i][j];
            }
            if (j != board[i].size() - 1) {
                cout << " ";
            }
        }
        if (i != board.size() - 1) {
            cout << endl;
        }
    }
}

void makeMove(vector<vector<char>>& board, int player, int row, int col) {
    char mark = (player == 0) ? 'x' : 'o';
    board[row][col] = mark;
}

bool findWinner(const vector<vector<char>>& board, char mark) {

    // this code checks to rows and columns to find 3 mathcing items
    for (int i = 0; i < 3; ++i) {
        if ((board[i][0] == mark && board[i][1] == mark && board[i][2] == mark) || (board[0][i] == mark && board[1][i] == mark && board[2][i] == mark)) {
            return true;
        }
    }
    // this code will look for a winner along the 2 main diagonals
    if ((board[0][0] == mark && board[1][1] == mark && board[2][2] == mark) || (board[0][2] == mark && board[1][1] == mark && board[2][0] == mark)) {
        return true;
    }

    // no winner has been found
    return false;
}

string terminationCheck(const vector<vector<char>>& board) {

    // booleans to check the games outcome
    bool xWins = findWinner(board, 'x');
    bool oWins = findWinner(board, 'o');
    bool draw = true;

    // Check the case where the board is blank
    for (const auto& row : board) {
        for (char cell : row) {
            if (cell == '.') {
                draw = false;
                break;
            }
        }
    }
    if (xWins) {
        return "X wins";
    } else if (oWins) {
        return "O wins";
    } else if (draw) {
        return "Draw";
    } else {
        return "In progress";
    }
}

int main() {
    vector<vector<char>> board(3, vector<char>(3, '.'));

    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            cin >> board[i][j];
        }
    }

    cout << terminationCheck(board);

    return 0;
}