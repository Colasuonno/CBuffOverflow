# Makefile

CC = gcc
CFLAGS = -Wall -Wextra -g -O0 -std=c99 -fno-stack-protector -m32 -no-pie -z execstack

SRC := $(wildcard *.c) $(wildcard */*.c)
TARGETS := $(SRC:.c=)

all: $(SRC)
	if [ ! -d "./bin" ]; then mkdir bin; fi
	$(foreach f, $(SRC), $(CC) $(CFLAGS) -o $(patsubst src/%.c, bin/%, $(f)) $(f);)

%: src/%.c
	if [ ! -d "./bin" ]; then mkdir bin; fi
	$(CC) $(CFLAGS) -o bin/$@ $<

clean:
	rm -f $(TARGETS)
