#include <stdio.h>
#include <string.h>

void doubleCall(void) {
  char buf[8];
  gets(buf);
  printf("%s\n", buf);
}

int main(void) {
  printf("Init Program\n");
  doubleCall();
  printf("End Program\n");

  return 0;
}