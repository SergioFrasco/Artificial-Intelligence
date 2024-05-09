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

int main() {
    vector<vector<char>> board(3, vector<char>(3, '.'));

    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            cin >> board[i][j];
        }
    }

    printBoard(board);

    return 0;
}
