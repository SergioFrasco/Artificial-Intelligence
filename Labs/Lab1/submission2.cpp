#include <iostream>
#include <string>
#include <limits>
using namespace std;

int main()
{


    char inputs[16];
    int blankpos = 0;

    for (int i = 0; i < 16; i++)
    {
        cin >> inputs[i];
        if (inputs[i] == '#'){
            blankpos = i;
        }
    }

    
    cin.ignore(numeric_limits<streamsize>::max(), '\n');

    string move;
    cin >> move;

    if (move == "UP"){
        int temp = inputs[blankpos];
        inputs[blankpos] = inputs[blankpos-4];
        inputs[blankpos-4] = temp;
    }

    if (move == "RIGHT"){

        int temp = inputs[blankpos];
        inputs[blankpos] = inputs[blankpos+1];
        inputs[blankpos+1] = temp;

    }

    if (move == "DOWN"){
        int temp = inputs[blankpos];
        inputs[blankpos] = inputs[blankpos+4];
        inputs[blankpos+4] = temp;
        
    }

    if (move == "LEFT"){
        int temp = inputs[blankpos];
        inputs[blankpos] = inputs[blankpos-1];
        inputs[blankpos-1] = temp;
        
    }

    for (int i = 0; i < 16; i++) {
        cout << inputs[i];
        if ((i + 1) % 4 == 0) {
            cout << endl; 
        }
        else{
            cout << " ";
        }
    }
}
