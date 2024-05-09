#include <iostream>
#include <fstream>
#include <string>
#include <limits>
#include <queue>
#include <array>
#include <set>
#include <vector>

using namespace std;

int expandedNodes;

struct PuzzleConfig
{
    array<char, 16> tiles;
    int blankpos;

    bool operator<(const PuzzleConfig &other) const
    {
        return tiles < other.tiles; 
    }

    int depth;

    PuzzleConfig &operator=(const PuzzleConfig &other)
    {
        if (this != &other) // Avoid self-assignment
        {
            tiles = other.tiles; // Perform a deep copy of the tiles array
        }
        return *this;
    }
};

void print(PuzzleConfig board)
{
    for (int j = 0; j < 16; j++)
    {
        if ((j + 1) % 4 == 0)
        {
            cout << board.tiles[j] << endl;
        }
        else
        {
            cout << board.tiles[j] << " ";
        }
    }
    cout << "--------------------------------------------------------------" << endl;
}

bool isGoalState(const PuzzleConfig &state)
{
    // Define the goal state
    const array<char, 16> goalTiles = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', '#'};

    // Check if the tiles in the current state match the goal state
    return state.tiles == goalTiles;
}

vector<PuzzleConfig> generateSuccessors(PuzzleConfig currentBoard)
{
    vector<char> possibleMoves;

    // UP
    if (currentBoard.blankpos - 4 >= 0)
    {
        possibleMoves.push_back('U');
    }

    // DOWN
    if (currentBoard.blankpos + 4 < 16)
    {
        possibleMoves.push_back('D');
    }

    // LEFT
    if (currentBoard.blankpos - 1 >= 0 && (currentBoard.blankpos - 1) % 4 != 3)
    {
        possibleMoves.push_back('L');
    }

    // RIGHT
    if (currentBoard.blankpos + 1 < 16 && (currentBoard.blankpos + 1) % 4 != 0)
    {
        possibleMoves.push_back('R');
    }

    vector<PuzzleConfig> successors;

    // for loop to build possible moves and generate new successor boards
    for (int i = 0; i < possibleMoves.size(); i++)
    {
        char move = possibleMoves[i];

        if (move == 'U')
        {
            PuzzleConfig newBoard(currentBoard);
            int temp = newBoard.tiles[newBoard.blankpos];
            newBoard.tiles[newBoard.blankpos] = newBoard.tiles[newBoard.blankpos - 4];
            newBoard.tiles[newBoard.blankpos - 4] = temp;
            // add the board
            newBoard.blankpos -= 4;
            newBoard.depth +=1;
            successors.push_back(newBoard);
        }
        else if (move == 'R')
        {
            PuzzleConfig newBoard(currentBoard);
            int temp = newBoard.tiles[newBoard.blankpos];
            newBoard.tiles[newBoard.blankpos] = newBoard.tiles[newBoard.blankpos + 1];
            newBoard.tiles[newBoard.blankpos + 1] = temp;
            // add the board
            newBoard.blankpos += 1;
            newBoard.depth +=1;
            successors.push_back(newBoard);
        }
        else if (move == 'D')
        {
            PuzzleConfig newBoard(currentBoard);
            int temp = newBoard.tiles[newBoard.blankpos];
            newBoard.tiles[newBoard.blankpos] = newBoard.tiles[newBoard.blankpos + 4];
            newBoard.tiles[newBoard.blankpos + 4] = temp;
            // add the board
            newBoard.blankpos += 4;
            newBoard.depth +=1;
            successors.push_back(newBoard);
        }
        else if (move == 'L')
        {
            PuzzleConfig newBoard(currentBoard);
            int temp = newBoard.tiles[newBoard.blankpos];
            newBoard.tiles[newBoard.blankpos] = newBoard.tiles[newBoard.blankpos - 1];
            newBoard.tiles[newBoard.blankpos - 1] = temp;
            // add the board
            newBoard.blankpos -= 1;
            newBoard.depth +=1;
            successors.push_back(newBoard);
        }
    }

    possibleMoves.clear(); // Free the vector of moves that are possible

    return successors;
}

int main()
{
    ifstream inputFile("puzzles.txt");
    ofstream outputFile("output.csv");

    if (!inputFile.is_open())
    {
        cerr << "Error: Unable to open input file." << endl;
        return 1;
    }

    if (!outputFile.is_open())
    {
        cerr << "Error: Unable to open output file." << endl;
        return 1;
    }

    while (inputFile)
    {
        // CODE TO INITIALIZE THE ORIGINAL BOARD
        expandedNodes = 0;
        PuzzleConfig initialConfig;
        initialConfig.depth = 0;

        char character;
        for (int i = 0; i < 16; i++)
        {
            inputFile >> character;

            if (character == '#')
            {
                initialConfig.blankpos = i;
            }
            initialConfig.tiles[i] = character;
        }

        queue<PuzzleConfig> boards;
        boards.push(initialConfig); // enqueue the starting board

        set<PuzzleConfig> Visited;     // create set for nodes weve visited
        Visited.insert(initialConfig); // mark starting node as visited

        while (!boards.empty())
        {
            expandedNodes += 1;
            PuzzleConfig currentState = boards.front();
            boards.pop();

            if (isGoalState(currentState))
            {
                outputFile << currentState.depth << "," << expandedNodes-2 << endl;
                break;
            }

            vector<PuzzleConfig> successors = generateSuccessors(currentState);
        
            for (const auto &successor : successors)
            {
                if (Visited.count(successor) == 0)
                {
                    Visited.insert(successor);
                    boards.push(successor);
                }
            }
        }
    }

    inputFile.close();
    outputFile.close();

    return 0;
}
