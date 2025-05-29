import os
import subprocess

MAX_TRY = 1000000
STARTING_SIZE = 100

PROGRAM_PATH = "./code_exec_no_size_known"

def find_buffer_size(to_exploit_program_path):
    for i in range(STARTING_SIZE, MAX_TRY, 5):
        try:
            payload = "A" * i
            proc = subprocess.Popen(
                [to_exploit_program_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = proc.communicate(input=payload)
            returncode = proc.returncode

            if returncode != 0:
                print "Program crashed at input size: %d" % i
                return i

        except Exception, e:
            print "Error at size %d: %s" % (i, str(e))
            return i

    print "No crash detected"
    return None

if __name__ == "__main__":
    buffer_size = find_buffer_size(PROGRAM_PATH)
    if buffer_size:
        print "Probabile dimensione del buffer: %d" % buffer_size
    else:
        print "Buffer overflow non rilevato."

