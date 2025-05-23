import os
import subprocess

MAX_TRY = 1000000
STARTING_SIZE = 100

PROGRAM_PATH = "./code_exec_no_size_known"

def find_buffer_size(to_exploit_program_path):
    for i in range(STARTING_SIZE, MAX_TRY, 5):
        try:
            payload = b"A" * i
            result = subprocess.run([to_exploit_program_path], input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            if result.returncode != 0:
                print(f"Program crashed at input size: {i}")
                return i
        except subprocess.TimeoutExpired:
            print(f"Timeout at size {i}, possible infinite loop or hang")
            return i
        except Exception as e:
            print(f"Error at size {i}: {e}")
            return i
    print("No crash detected")
    return None

if __name__ == "__main__":
    buffer_size = find_buffer_size(PROGRAM_PATH)
    if buffer_size:
        print(f"Probabile dimensione del buffer: {buffer_size}")
    else:
        print("Buffer overflow non rilevato.")
