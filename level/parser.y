%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylex();
extern int yyparse();
extern FILE *yyin;
void yyerror(char *s);

// Tabela de símbolos (simplificada)
typedef struct symbol {
    char *name;
    int type;
} symbol;

symbol *symtab[100];
int symtab_index = 0;

%}

%union {
    int num;
    char *str;
}

// Tokens
%token <str> IDENTIFIER
%token <num> NUMBER_LITERAL
%token <str> STRING_LITERAL
%token TEXT NUMBER_TYPE BOOLEAN_TYPE ARRAY_TYPE
%token FUNC ENTITY IF ELSE UNTIL DURING RETURN
%token MOVE ATTACK GATHER USE SAY WAIT
%token TRUE FALSE LEN
%token AND OR EQ NE LT GT LE GE
%token ASSIGN PLUS MINUS TIMES DIVIDE
%token LPAREN RPAREN LBRACE RBRACE LBRACKET RBRACKET
%token COLON SEMICOLON COMMA

%start program

%%

program: /* vazio */
    | program declaration
    | program command
    ;

declaration: variable_declaration
    | func_declaration
    | entity_declaration
    ;

variable_declaration: IDENTIFIER COLON type ASSIGN expression SEMICOLON
    {
        printf("Variável declarada: %s\n", $1);
        free($1);
    }
    ;

type: base_type
    | type LBRACKET RBRACKET
    ;

base_type: TEXT
    | NUMBER_TYPE
    | BOOLEAN_TYPE
    | ARRAY_TYPE
    ;

func_declaration: FUNC IDENTIFIER LPAREN parameters RPAREN optional_return_type LBRACE commands RBRACE
    {
        printf("Função declarada: %s\n", $2);
        free($2);
    }
    ;

optional_return_type: /* vazio */
    | COLON type
    ;

parameters: /* vazio */
    | parameter_list
    ;

parameter_list: parameter
    | parameter_list COMMA parameter
    ;

parameter: IDENTIFIER COLON type
    ;

entity_declaration: ENTITY IDENTIFIER LBRACE entity_members RBRACE
    {
        printf("Entidade declarada: %s\n", $2);
        free($2);
    }
    ;

entity_members: /* vazio */
    | entity_members entity_member
    ;

entity_member: variable_declaration
    | func_declaration
    ;

commands: /* vazio */
    | commands command
    ;

command: assignment
    | conditional
    | loop
    | action
    | return_command
    | block
    ;

assignment: IDENTIFIER ASSIGN expression SEMICOLON
    {
        printf("Atribuição: %s\n", $1);
        free($1);
    }
    | IDENTIFIER LBRACKET expression RBRACKET ASSIGN expression SEMICOLON
    {
        printf("Atribuição de array: %s\n", $1);
        free($1);
    }
    ;

conditional: IF LPAREN expression RPAREN block optional_else
    {
        printf("Condicional if\n");
    }
    ;

optional_else: /* vazio */
    | ELSE block
    ;

loop: UNTIL LPAREN expression RPAREN block
    {
        printf("Loop until\n");
    }
    | DURING LPAREN variable_declaration expression SEMICOLON assignment RPAREN block
    {
        printf("Loop during\n");
    }
    ;

return_command: RETURN optional_expression SEMICOLON
    {
        printf("Comando return\n");
    }
    ;

optional_expression: /* vazio */
    | expression
    ;

block: LBRACE commands RBRACE
    ;

action: MOVE LPAREN expression RPAREN SEMICOLON
    {
        printf("Ação: move\n");
    }
    | ATTACK LPAREN optional_expression RPAREN SEMICOLON
    {
        printf("Ação: attack\n");
    }
    | GATHER LPAREN IDENTIFIER RPAREN SEMICOLON
    {
        printf("Ação: gather %s\n", $3);
        free($3);
    }
    | USE LPAREN IDENTIFIER RPAREN SEMICOLON
    {
        printf("Ação: use %s\n", $3);
        free($3);
    }
    | SAY LPAREN STRING_LITERAL RPAREN SEMICOLON
    {
        printf("Ação: say '%s'\n", $3);
        free($3);
    }
    | WAIT LPAREN NUMBER_LITERAL RPAREN SEMICOLON
    {
        printf("Ação: wait %d\n", $3);
    }
    ;

expression: logical_expression
    ;

logical_expression: relational_expression
    | logical_expression AND relational_expression
    | logical_expression OR relational_expression
    ;

relational_expression: arithmetic_expression
    | relational_expression EQ arithmetic_expression
    | relational_expression NE arithmetic_expression
    | relational_expression LT arithmetic_expression
    | relational_expression GT arithmetic_expression
    | relational_expression LE arithmetic_expression
    | relational_expression GE arithmetic_expression
    ;

arithmetic_expression: term
    | arithmetic_expression PLUS term
    | arithmetic_expression MINUS term
    ;

term: factor
    | term TIMES factor
    | term DIVIDE factor
    ;

factor: literal
    | IDENTIFIER
    | array_access
    | LPAREN expression RPAREN
    | len_call
    ;

array_access: IDENTIFIER LBRACKET expression RBRACKET
    {
        printf("Acesso a array: %s\n", $1);
        free($1);
    }
    ;

len_call: LEN LPAREN IDENTIFIER RPAREN
    {
        printf("Chamada len: %s\n", $3);
        free($3);
    }
    ;

literal: NUMBER_LITERAL
    {
        printf("Número: %d\n", $1);
    }
    | boolean
    | STRING_LITERAL
    {
        printf("String: '%s'\n", $1);
        free($1);
    }
    | array_literal
    ;

array_literal: LBRACKET optional_expression_list RBRACKET
    {
        printf("Array literal\n");
    }
    ;

optional_expression_list: /* vazio */
    | expression_list
    ;

expression_list: expression
    | expression_list COMMA expression
    ;

boolean: TRUE
    {
        printf("Boolean: true\n");
    }
    | FALSE
    {
        printf("Boolean: false\n");
    }
    ;

%%

void yyerror(char *s) {
    extern char *yytext;
    fprintf(stderr, "Erro sintático: %s no token '%s'\n", s, yytext);
}

int main(int argc, char **argv) {
    if (argc > 1) {
        yyin = fopen(argv[1], "r");
        if (!yyin) {
            perror("Erro ao abrir o arquivo");
            return 1;
        }
    } else {
        printf("Uso: %s <arquivo.level>\n", argv[0]);
        return 1;
    }

    printf("Iniciando análise do arquivo...\n");
    
    if (yyparse() == 0) {
        printf("Análise sintática concluída com sucesso!\n");
    } else {
        printf("Falha na análise sintática.\n");
        return 1;
    }

    fclose(yyin);
    return 0;
}