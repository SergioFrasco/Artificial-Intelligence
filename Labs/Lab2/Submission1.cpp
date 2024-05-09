#include <iostream>
#include <vector>
#include <sstream>

using namespace std;

// ------Code to implement a IED algorithm----------
// Define the structure for each cell
struct boardItem
{
    int red;
    int blue;
    bool dominated = false;
};

// Function to parse input string into a boardItem struct
boardItem parseInput(const string &input)
{
    boardItem item;
    stringstream ss(input);
    char comma;
    ss >> item.red >> comma >> item.blue;
    return item;
}

// Code to find a row which has not been dominated
vector<int> findAvailableRow(vector<vector<boardItem>> grid)
{
    vector<int> rowIndices;
    int rowIndex1 = -1; // Initialize rowIndex1 to an invalid index
    int rowIndex2 = -1;

    for (int i = 0; i < grid.size(); i++)
    {
        bool rowDominated = true; // Assume initially that the row is dominated
        for (int j = 0; j < grid.size(); j++)
        {
            if (grid[i][j].dominated == false)
            {
                rowDominated = false; // If any item in the row is not dominated, mark the row as not dominated
                break;                // No need to check further if one item is not dominated
            }
        }
        // If the row is not dominated
        if (!rowDominated)
        {
            if (rowIndex1 == -1)
            {
                rowIndex1 = i;
                rowIndices.push_back(rowIndex1);
            }
            else
            {
                rowIndex2 = i;
                rowIndices.push_back(rowIndex2);
                break; // Exit the loop once the second available row is found
            }
        }
    }

    // If only one non-dominated row is found, mark the second index as -1
    if (rowIndices.size() == 1)
    {
        rowIndices.push_back(-1);
    }

    return rowIndices;
}

// Code to find a column which has not been dominated
vector<int> findAvailableCol(vector<vector<boardItem>> grid)
{
    vector<int> colIndices;
    int colIndex1 = -1; // Initialize colIndex1 to an invalid index
    int colIndex2 = -1;

    for (int j = 0; j < grid.size(); j++)
    {
        bool colDominated = true; // Assume initially that the column is dominated
        for (int i = 0; i < grid.size(); i++)
        {
            if (grid[i][j].dominated == false)
            {
                colDominated = false; // If any item in the column is not dominated, mark the column as not dominated
                break;                // No need to check further if one item is not dominated
            }
        }
        // If the column is not dominated
        if (!colDominated)
        {
            if (colIndex1 == -1)
            {
                colIndex1 = j;
                colIndices.push_back(colIndex1);
            }
            else
            {
                colIndex2 = j;
                colIndices.push_back(colIndex2);
                break; // Exit the loop once the second available column is found
            }
        }
    }

    // If only one non-dominated column is found, mark the second index as -1
    if (colIndices.size() == 1)
    {
        colIndices.push_back(-1);
    }

    return colIndices;
}

// Code to compare two rows and mark the non dominant one as dominated
void markNonDominantRow(vector<vector<boardItem>> &grid, int row1, int row2)
{

    if (row1 < 0 || row1 >= grid.size() || row2 < 0 || row2 >= grid.size())
    {
        cout << "Row index out of bounds";
        return;
    }

    // Compare red values in corresponding columns
    for (int i = 0; i < grid[row1].size(); i++)
    {
        if (grid[row1][i].red > grid[row2][i].red && !grid[row1][i].dominated && !grid[row2][i].dominated)
        {
            // If any red value in row1 is greater or equal to the corresponding red value in row2,
            // then row2 is not dominant over row1
            // Mark row2 as dominated
            for (int j = 0; j < grid[row2].size(); j++)
            {
                grid[row2][j].dominated = true;
            }
            return; // No need to continue further
        }
    }

    // If we reach here, row2 is dominant over row1
    // Mark row1 as dominated
    for (int j = 0; j < grid[row1].size(); j++)
    {
        grid[row1][j].dominated = true;
    }
}

// Code to compare two cols and mark the non dominant one as dominated
void markNonDominantCol(vector<vector<boardItem>> &grid, int col1, int col2)
{
    // cout <<" Comparing col 1: "<< col1<<endl;
    //  cout <<" and col 2: "<< col2<<endl;
    // Check if either column index is out of bounds
    if (col1 < 0 || col1 >= grid.size() || col2 < 0 || col2 >= grid.size())
    {
        cout << "Column index out of bounds";
        return;
    }

    // Compare blue values in corresponding rows
    for (int i = 0; i < grid.size(); i++)
    {
        // cout <<"col 1 with value: "<< grid[i][col1].blue<<endl;
        // cout <<"col 2: with value: "<< grid[i][col2].blue<<endl;
        if (grid[i][col1].blue > grid[i][col2].blue && !grid[i][col1].dominated && !grid[i][col2].dominated) //AND NOT DOMINATWED
        {
            // If any blue value in col1 is greater or equal to the corresponding blue value in col2,
            // then col2 is not dominant over col1
            // Mark col2 as dominated
            for (int j = 0; j < grid.size(); j++)
            {
                grid[j][col2].dominated = true;
            }

            // cout << "Decision " << col1 << " Dominates" << endl;
            return; // No need to continue further
        }
    }

    // If we reach here, col2 is dominant over col1
    // Mark col1 as dominated
    for (int j = 0; j < grid.size(); j++)
    {
        grid[j][col1].dominated = true;
    }
    // cout << "Decision " << col2 << " Dominates";
}

// Function to find the final solution
void findGoal(const vector<vector<boardItem>> &grid)
{
    // Iterate through the board to find the item which is not marked as dominated
    for (const auto &row : grid)
    {
        for (const auto &item : row)
        {
            if (!item.dominated)
            {
                // Print out the red and blue values of the non-dominated item
                cout << item.red << "," << item.blue << endl;
                return; // We found the goal, so we can exit the function
            }
        }
    }
    // If no non-dominated item is found, print a message indicating that
    cout << "No non-dominated item found!" << endl;
}

int main()
{
    int n; // Size of the grid
    // cout << "Enter the size of the grid: ";
    cin >> n;

    vector<vector<boardItem>> grid(n, vector<boardItem>(n)); // Create a 2D vector grid

    // Input loop to fill the grid
    // cout << "Enter the grid items:\n";
    for (int i = 0; i < n; ++i)
    {
        for (int j = 0; j < n; ++j)
        {
            string input;
            cin >> input;
            grid[i][j] = parseInput(input);
        }
    }

    // Display the grid
    // cout << "Grid:\n";
    // for (int i = 0; i < n; ++i)
    // {
    //     for (int j = 0; j < n; ++j)
    //     {
    //         cout << "(" << grid[i][j].red << "," << grid[i][j].blue << ") ";
    //     }
    //     cout << endl;
    // }

    // main loop to do the IED algorithm
    bool rowTurn = true;
    while (true)
    {
        if (rowTurn == true)
        { // It's the row's turn
            vector<int> rowIndices = findAvailableRow(grid);

            if (rowIndices[1] == -1)
            {
                // cout << "Row: " << rowIndices[0] << endl;
                findGoal(grid);
                break; // goal found
            }

            markNonDominantRow(grid, rowIndices[0], rowIndices[1]);

            // Debugging
            // cout << "Grid:\n";
            // for (int i = 0; i < n; ++i)
            // {
            //     // for (int j = 0; j < n; ++j)
            //     // {
            //     //     if(grid[i][j].dominated == true){
            //     //         cout << "(" << 'x' << "," << 'x' << ") ";
            //     //     }
            //     //     else{
            //     //         cout << "(" << grid[i][j].red << "," << grid[i][j].blue << ") ";
            //     //     }
                    
            //     // }
            //     // cout << endl;
            // }


            rowTurn = false; // Now switch to a column turn
        }

        else
        { // It's the col's turn
            vector<int> colIndices = findAvailableCol(grid);

            if (colIndices[1] == -1)
            {
                cout << "Col: " << colIndices[0] << endl;
                findGoal(grid);
                break; // goal found
            }
            markNonDominantCol(grid, colIndices[0], colIndices[1]);

            // Debugging
            // cout << "Grid:\n";
            // for (int i = 0; i < n; ++i)
            // {
            //     for (int j = 0; j < n; ++j)
            //     {
            //         if(grid[i][j].dominated == true){
            //             cout << "(" << 'x' << "," << 'x' << ") ";
            //         }
            //         else{
            //             cout << "(" << grid[i][j].red << "," << grid[i][j].blue << ") ";
            //         }
                    
            //     }
            //     cout << endl;
            // }

            
            rowTurn = true; // Now switch to a column turn
        }
    }
    return 0;
}
