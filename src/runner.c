#include <stdio.h>
#include <stdint.h>
extern int64_t code_starts_here() asm("code_starts_here");

int main(int argc, char** argv) {
  int64_t result = code_starts_here();
  
  if(result&1){
	  printf("%ld\n", result/2);
  }else if (result==0xFFFFFFFFFFFFFFFEULL){
  	  printf("true\n");
	  
  }else if (result==0x7FFFFFFFFFFFFFFEULL){
	  printf("false\n");
  }else{
	  printf("error: value not representable\n");
  }
	  

  return 0;
}

