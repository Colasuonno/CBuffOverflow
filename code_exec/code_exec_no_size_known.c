#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <stdio.h>

int toExploit() {
    char buff[500];
    gets(buff);
    printf("%s\n", buff);
}


int main() {
    printf("Init Program\n");
    toExploit();
    printf("End Program\n");
    return 0;
}
