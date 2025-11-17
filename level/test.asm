section .data
  format_out: db "%d", 10, 0
  format_in: db "%d", 0
  scan_int: dd 0

section .text
  extern printf
  extern scanf
  global _start

_start:
  push ebp
  mov ebp, esp


  mov esp, ebp
  pop ebp
  mov eax, 1
  xor ebx, ebx
  int 0x80
