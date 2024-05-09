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
    int depth;
    int h1;
    int g;

    bool operator<(const PuzzleConfig &other) const
    {
        return g > other.g; // Note the change to prioritize lower costs
    }
};

void print(const PuzzleConfig &board)
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
    cout << "depth: " << board.depth << endl;
    cout << "h1: " << board.h1 << endl;
    cout << "g: " << board.g << endl;
    cout << "--------------------------------------------------------------" << endl;
}

bool isGoalState(const PuzzleConfig &state)
{
    const array<char, 16> goalTiles = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', '#'};
    return state.tiles == goalTiles;
}

int calculateHeuristic(const PuzzleConfig &currentBoard)
{
    int h1 = 0;
    const array<char, 16> goalTiles = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', '#'};
    for (int i = 0; i < 16; i++)
    {
        if (goalTiles[i] != currentBoard.tiles[i] && currentBoard.tiles[i] != '#')
        {
            h1 += 1;
        }
    }
    return h1;
}

vector<char> findPossibleMoves(const PuzzleConfig &currentBoard)
{
    int row = currentBoard.blankpos / 4;
    int col = currentBoard.blankpos % 4;

    vector<char> possibleMoves;
    if (row - 1 >= 0)
    {
        possibleMoves.push_back('U');
    }
    if (row + 1 < 4)
    {
        possibleMoves.push_back('D');
    }
    if (col - 1 >= 0)
    {
        possibleMoves.push_back('L');
    }
    if (col + 1 < 4)
    {
        possibleMoves.push_back('R');
    }

    return possibleMoves;
}

vector<PuzzleConfig> generateSuccessors(const PuzzleConfig &currentBoard)
{
    vector<char> possibleMoves = findPossibleMoves(currentBoard);
    vector<PuzzleConfig> successors;

    for (const auto &move : possibleMoves)
    {
        PuzzleConfig newBoard = currentBoard;
        int newPos;
        switch (move)
        {
        case 'U':
            newPos = newBoard.blankpos - 4;
            break;
        case 'D':
            newPos = newBoard.blankpos + 4;
            break;
        case 'L':
            newPos = newBoard.blankpos - 1;
            break;
        case 'R':
            newPos = newBoard.blankpos + 1;
            break;
        }

        swap(newBoard.tiles[newBoard.blankpos], newBoard.tiles[newPos]);
        newBoard.blankpos = newPos;
        newBoard.depth += 1;
        newBoard.h1 = calculateHeuristic(newBoard);
        newBoard.g = newBoard.depth + newBoard.h1;
        successors.push_back(newBoard);
    }

    return successors;
}

int main()
{
    ifstream inputFile("puzzles.txt");
    ofstream outputFile("output1.csv");

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

        initialConfig.h1 = calculateHeuristic(initialConfig);
        initialConfig.g = initialConfig.depth + initialConfig.h1;

        priority_queue<PuzzleConfig> boards;
        set<array<char, 16>> Visited;

        boards.push(initialConfig);
        expandedNodes = 0;

        while (!boards.empty())
        {
            
            PuzzleConfig currentState = boards.top();
            boards.pop();

            if (isGoalState(currentState))
            {
                outputFile << currentState.depth << "," << expandedNodes  << endl;
                break;
            }

            Visited.insert(currentState.tiles);

            vector<PuzzleConfig> successors = generateSuccessors(currentState);
            for (const auto &successor : successors)
            {
                if (Visited.count(successor.tiles) == 0)
                {
                    boards.push(successor);
                    Visited.insert(successor.tiles); // Update visited set
                    expandedNodes += 1;
                }
            }
        }
    }

    inputFile.close();
    outputFile.close();

    return 0;
}
