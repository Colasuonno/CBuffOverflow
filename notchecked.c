#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/*
Not checked size of argv[1], Buffer overflow with argv[1] length > 8 char
*/

int main(int argc, char* argv[]){

    char inputString[8];
    
    if (argc < 2){
        printf("You need to specify the echo string, /notchecked <string>\n");
        exit(EXIT_FAILURE);
    }

    strcpy(inputString, argv[1]);
    printf("Echo %s\n", inputString);
}