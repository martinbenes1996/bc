
CC = gcc
CFLAGS = -fPIC -pedantic -Wall -Wextra -O2 -g
LDFLAGS = -shared

SRCS = $(wildcard *.h)
TARGET = lib.so

.PHONY: all
all: $(TARGET)

$(TARGET): $(SRCS)
	@echo "Linking lib.so.";\
	$(CC) $(LDFLAGS) $(CFLAGS) $^ -o $@

.PHONY: clean
clean:
	@echo "Cleaning lib/ subdirectory.";\
	rm -rf $(TARGET)