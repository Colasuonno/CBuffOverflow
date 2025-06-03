#include <stdio.h>
#include <string.h>

void specialPrint(char *text) {
  char buf[500];
  strcpy(buf, text);
  printf("%s\n", buf);
}

int main(char argc, char *argv[]) {
  printf("Init Program\n");
  specialPrint(argv[1]);
  printf("End Program\n");
  return 0;
}