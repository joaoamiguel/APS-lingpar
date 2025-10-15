/* A Bison parser, made by GNU Bison 3.8.2.  */

/* Bison interface for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2015, 2018-2021 Free Software Foundation,
   Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* DO NOT RELY ON FEATURES THAT ARE NOT DOCUMENTED in the manual,
   especially those whose name start with YY_ or yy_.  They are
   private implementation details that can be changed or removed.  */

#ifndef YY_YY_PARSER_TAB_H_INCLUDED
# define YY_YY_PARSER_TAB_H_INCLUDED
/* Debug traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif
#if YYDEBUG
extern int yydebug;
#endif

/* Token kinds.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
  enum yytokentype
  {
    YYEMPTY = -2,
    YYEOF = 0,                     /* "end of file"  */
    YYerror = 256,                 /* error  */
    YYUNDEF = 257,                 /* "invalid token"  */
    IDENTIFIER = 258,              /* IDENTIFIER  */
    NUMBER_LITERAL = 259,          /* NUMBER_LITERAL  */
    STRING_LITERAL = 260,          /* STRING_LITERAL  */
    TEXT = 261,                    /* TEXT  */
    NUMBER_TYPE = 262,             /* NUMBER_TYPE  */
    BOOLEAN_TYPE = 263,            /* BOOLEAN_TYPE  */
    ARRAY_TYPE = 264,              /* ARRAY_TYPE  */
    FUNC = 265,                    /* FUNC  */
    ENTITY = 266,                  /* ENTITY  */
    IF = 267,                      /* IF  */
    ELSE = 268,                    /* ELSE  */
    UNTIL = 269,                   /* UNTIL  */
    DURING = 270,                  /* DURING  */
    RETURN = 271,                  /* RETURN  */
    MOVE = 272,                    /* MOVE  */
    ATTACK = 273,                  /* ATTACK  */
    GATHER = 274,                  /* GATHER  */
    USE = 275,                     /* USE  */
    SAY = 276,                     /* SAY  */
    WAIT = 277,                    /* WAIT  */
    TRUE = 278,                    /* TRUE  */
    FALSE = 279,                   /* FALSE  */
    LEN = 280,                     /* LEN  */
    AND = 281,                     /* AND  */
    OR = 282,                      /* OR  */
    EQ = 283,                      /* EQ  */
    NE = 284,                      /* NE  */
    LT = 285,                      /* LT  */
    GT = 286,                      /* GT  */
    LE = 287,                      /* LE  */
    GE = 288,                      /* GE  */
    ASSIGN = 289,                  /* ASSIGN  */
    PLUS = 290,                    /* PLUS  */
    MINUS = 291,                   /* MINUS  */
    TIMES = 292,                   /* TIMES  */
    DIVIDE = 293,                  /* DIVIDE  */
    LPAREN = 294,                  /* LPAREN  */
    RPAREN = 295,                  /* RPAREN  */
    LBRACE = 296,                  /* LBRACE  */
    RBRACE = 297,                  /* RBRACE  */
    LBRACKET = 298,                /* LBRACKET  */
    RBRACKET = 299,                /* RBRACKET  */
    COLON = 300,                   /* COLON  */
    SEMICOLON = 301,               /* SEMICOLON  */
    COMMA = 302                    /* COMMA  */
  };
  typedef enum yytokentype yytoken_kind_t;
#endif

/* Value type.  */
#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
union YYSTYPE
{
#line 22 "parser.y"

    int num;
    char *str;

#line 116 "parser.tab.h"

};
typedef union YYSTYPE YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE yylval;


int yyparse (void);


#endif /* !YY_YY_PARSER_TAB_H_INCLUDED  */
