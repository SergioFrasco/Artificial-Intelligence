#include <iostream>
#include <vector>

using namespace std;


bool findWinner(const vector<vector<char>>& board, char mark) {

    // this code checks to rows and columns to find 3 mathcing items
    for (int i = 0; i < 3; ++i) {
        if ((board[i][0] == mark && board[i][1] == mark && board[i][2] == mark) ||(board[0][i] == mark && board[1][i] == mark && board[2][i] == mark)) {
            return true;
        }
    }
    // this code will look for a winner along the 2 main diagonals
    if ((board[0][0] == mark && board[1][1] == mark && board[2][2] == mark) ||(board[0][2] == mark && board[1][1] == mark && board[2][0] == mark)) {
        return true;
    }

    // no winner 
    return false;
}

// check if board is full and there is no winner
bool isGameDraw(const vector<vector<char>> &board){
    for (const auto &row : board)
    {
        for (char cell : row)
        {
            if (cell == '.')
            {
                return false; 
            }
        }
    }
    return true;
}

char findPlayerTurn(const vector<vector<char>> &board){
    // counters to keep trac
    int xCount = 0;
    int oCount = 0;

    // count to see who has the most plays
    for (const auto &row : board){
        for (char cell : row){
            if (cell == 'x'){
                xCount++;
            }
            else if (cell == 'o'){
                oCount++;
            }
        }
    }

    // if the number of x's is equal to the number of o's, we always know its x's turn
    if (xCount == oCount){
        return 'x';
    }
    else{
        return 'o';
    }
}

// Recursive call function
string findGameWinner(const vector<vector<char>> &board)
{
    char turn = findPlayerTurn(board);

    // Check if the current player can win
    if (findWinner(board, turn)){
        if (turn == 'x'){
            return "X wins";
        }
        else{
            return "O wins";;
        }
       
    }

    // Check if the game is a draw, hence there are no winners and the board is full
    if (isGameDraw(board)){
        return "Draw";
    }

    
    string bestOutcome;
    if (turn == 'x'){
        bestOutcome = "O wins";
    }
    else{
       bestOutcome = "X wins";
    }
     
    for (int i = 0; i < 3; i++){
        for (int j = 0; j < 3; j++){
            if (board[i][j] == '.'){
                // Creating a copy of the board
                vector<vector<char>> newBoard = board;
                newBoard[i][j] = turn;
                string outcome = findGameWinner(newBoard); //Recursive call to find the winner, first recursive ever :D
                
                // Update outcome for the current player
                if (turn == 'x'){
                    if (outcome == "X wins"){
                        return outcome; // so its x's trun and x wins is the outcome
                    }
                    else if (outcome != "Draw" && outcome != "O wins"){
                        bestOutcome = outcome;
                    }
                }
                else {
                    if (outcome == "O wins"){
                        return outcome; // its o's turn and o wins is the outcome
                    }
                    else if (outcome != "Draw" && outcome != "X wins"){
                        bestOutcome = outcome;
                    }
                }
            }
        }
    }

    return bestOutcome; 
}

// this will just check if the board is empty on start
bool checkDraw(const vector<vector<char>> &board){
    bool isEmpty = true; //bool to flag if the board is empty
    for (const auto &row : board){
        for (char cell : row){
            if (cell != '.'){
                isEmpty = false;
                break;
            }
        }
        if (!isEmpty){
            break;
        }
    }
    if (isEmpty)
    {
        cout << "Draw" << endl;
        return true;
    }
    else{
        return false;
    }
}

int main(){
    vector<vector<char>> board(3, vector<char>(3));
    string input;
    cin >> input;

    // populate the board
    for (int i = 0; i < 9; i++){
        int row = i / 3;
        int col = i % 3;
        board[row][col] = input[i];
    }

    
    if (checkDraw(board)){
        return 0; // board is empty
    }
    else{
        cout << findGameWinner(board) << endl; // run the perfect play algorithm
    }

    return 0;
}
