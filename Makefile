# Makefile

CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99 -fno-stack-protector -m32 -no-pie -z execstack

SRC := $(wildcard *.c) $(wildcard */*.c)
TARGETS := $(SRC:.c=)

all: $(TARGETS)

%: %.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(TARGETS)
