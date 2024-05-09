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

    // UP
    if(blankpos-4 >= 0){
        cout << "UP" << endl;
    }
    // DOWN
    if(blankpos+4 <= 15){
        cout << "DOWN" << endl;
    }
    // LEFT
    if(blankpos-1 >= 0 && (blankpos-1)%4 != 3){
        cout << "LEFT" << endl;
    }
    // RIGHT
    if(blankpos+1 <= 15 && (blankpos+1)%4 != 0){
        cout << "RIGHT" << endl;
    }


}
