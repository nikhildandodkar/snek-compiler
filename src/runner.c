#include <stdio.h>

extern int code_starts_here() asm("code_starts_here");

int main(int argc, char** argv) {
  int result = code_starts_here();
  printf("%d\n", result);
  return 0;
}

