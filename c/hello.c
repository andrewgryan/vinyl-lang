
#include<stdio.h>

int foo() {
  return 42;
}

int bar() {
  return foo();
}

int main() {
  printf("Hello, World!");
  return bar();
}
