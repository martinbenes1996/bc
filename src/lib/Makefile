
CC = gcc
CFLAGS = -std=gnu99 -fPIC -pedantic -Wall -Wextra -O2 -g
LDFLAGS = -shared

HEAD = $(wildcard *.h)	
SRC = $(wildcard *.c)
TARGET = libglobals.so

.PHONY: all
all: $(TARGET)

$(TARGET): $(SRC)
	@echo "Linking globals.so.";\
	$(CC) $(LDFLAGS) $(CFLAGS) $^ -o $@

.PHONY: clean
clean:
	@echo "Cleaning lib/ subdirectory.";\
	rm -rf $(TARGET)