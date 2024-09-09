#ifndef EXAMPLE_H
#define EXAMPLE_H

// --------------------------------------------------------------

int max(int a, int b, int c){
    int max = (a > b) ? (a > c ? a : c) : (b > c ? b : c);
    return max;
}

int min(int a, int b, int c){
    int min = (a < b) ? (a < c ? a : c) : (b < c ? b : c);
    return min;
}

#endif