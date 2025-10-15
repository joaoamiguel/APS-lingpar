CC = gcc
CFLAGS = -g

all: level_compiler

parser.tab.c parser.tab.h: parser.y
	bison -d parser.y

lex.yy.c: lexer.l parser.tab.h
	flex lexer.l

level_compiler: parser.tab.c lex.yy.c
	$(CC) $(CFLAGS) -o $@ parser.tab.c lex.yy.c -lfl

clean:
	rm -f level_compiler lex.yy.c parser.tab.c parser.tab.h parser.output

.PHONY: all clean
