%{
#include "parser.tab.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void yyerror(char *s);
%}

%option noyywrap

DELIM   [ \t\r\n]
WS      {DELIM}+
DIGIT   [0-9]
LETTER  [a-zA-Z]
ID      {LETTER}({LETTER}|{DIGIT}|_)*
NUMBER  {DIGIT}+
STRING  \"([^\"\\]|\\.)*\"

%%

{WS}        { /* Ignorar espaços em branco */ }

"text"      { return TEXT; }
"number"    { return NUMBER_TYPE; }
"boolean"   { return BOOLEAN_TYPE; }
"array"     { return ARRAY_TYPE; }
"func"      { return FUNC; }
"entity"    { return ENTITY; }
"if"        { return IF; }
"else"      { return ELSE; }
"until"     { return UNTIL; }
"during"    { return DURING; }
"return"    { return RETURN; }
"move"      { return MOVE; }
"attack"    { return ATTACK; }
"gather"    { return GATHER; }
"use"       { return USE; }
"say"       { return SAY; }
"wait"      { return WAIT; }
"true"      { return TRUE; }
"false"     { return FALSE; }
"len"       { return LEN; }

"&&"        { return AND; }
"||"        { return OR; }
"=="        { return EQ; }
"!="        { return NE; }
"<"         { return LT; }
">"         { return GT; }
"<="        { return LE; }
">="        { return GE; }
"="         { return ASSIGN; }
"+"         { return PLUS; }
"-"         { return MINUS; }
"*"         { return TIMES; }
"/"         { return DIVIDE; }
"("         { return LPAREN; }
")"         { return RPAREN; }
"{"         { return LBRACE; }
"}"         { return RBRACE; }
"["         { return LBRACKET; }
"]"         { return RBRACKET; }
":"         { return COLON; }
";"         { return SEMICOLON; }
","         { return COMMA; }

{ID}        { 
                yylval.str = strdup(yytext); 
                return IDENTIFIER; 
            }
{NUMBER}    { 
                yylval.num = atoi(yytext); 
                return NUMBER_LITERAL; 
            }
{STRING}    { 
                // Remove as aspas
                yylval.str = strdup(yytext+1);
                yylval.str[strlen(yylval.str)-1] = '\0';
                return STRING_LITERAL; 
            }

.           { 
                fprintf(stderr, "Erro léxico: caractere inválido '%c'\n", yytext[0]); 
                exit(1);
            }

%%