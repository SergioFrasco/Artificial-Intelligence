#include <iostream>
using namespace std;

int main()
{

    char inputs[16];

    for (int i = 0; i < 16; i++)
    {
        cin >> inputs[i];
    }

    for (int i = 0; i < 16; i++) {
        cout << inputs[i] ;
        if ((i + 1) % 4 == 0) {
            cout << endl; 
        }
        else{
          cout << ' ';  
        }
    }
}
