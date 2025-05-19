# C Buffer Overflow guide

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

