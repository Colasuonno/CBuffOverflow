# Makefile

CC = gcc
CFLAGS = -Wall -Wextra -O2
SRC = $(wildcard *.c)
TARGETS = $(SRC:.c=)

all: $(TARGETS)

%: %.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(TARGETS)
