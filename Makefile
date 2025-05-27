# Makefile

CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99 -fno-stack-protector -no-pie -z execstack
SRC := $(wildcard src/*.c)
TARGETS := $(patsubst src/%.c, bin/%, $(SRC))

all: $(SRC)
	$(foreach f, $(SRC), $(CC) $(CFLAGS) -o $(patsubst src/%.c, bin/%, $(f)) $(f);)

%: src/%.c
	$(CC) $(CFLAGS) -o bin/$@ $<

clean:
	rm -f $(TARGETS)
