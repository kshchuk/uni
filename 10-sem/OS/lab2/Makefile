# FS viewer variant 4 — macOS ARM64: asm core + Objective-C GUI
ARCH ?= arm64
TARGET = pfs

CFLAGS = -arch $(ARCH) -Wall -O1
OBJCFLAGS = $(CFLAGS) -fobjc-arc
LDFLAGS = -arch $(ARCH) -framework Cocoa -framework Foundation

ASM_SRCS = src/fs.s src/png_ihdr.s src/render.s
C_SRCS = src/main.m src/AppDelegate.m

OBJS = $(ASM_SRCS:.s=.o) $(C_SRCS:.m=.o)

.PHONY: all clean run

all: $(TARGET)

$(TARGET): $(OBJS)
	clang $(LDFLAGS) -o $@ $(OBJS)

src/%.o: src/%.s
	clang $(CFLAGS) -c -o $@ $<

src/%.o: src/%.m
	clang $(OBJCFLAGS) -c -o $@ $<

clean:
	rm -f $(TARGET) src/*.o

run: $(TARGET)
	./$(TARGET)
