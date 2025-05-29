# Makefile

CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99 -fno-stack-protector -m32 -no-pie -z execstack

SRC := $(wildcard *.c) $(wildcard */*.c)
TARGETS := $(SRC:.c=)

all: $(SRC)
	$(foreach f, $(SRC), $(CC) $(CFLAGS) -o $(patsubst src/%.c, bin/%, $(f)) $(f);)

%: src/%.c
	$(CC) $(CFLAGS) -o bin/$@ $<

clean:
	rm -f $(TARGETS)
