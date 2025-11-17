#!/usr/bin/env python3
import sys
import re
import os
import time

class Code:
    instructions = []
    @staticmethod
    def append(code: str) -> None:
        Code.instructions.append(code)
    @staticmethod
    def dump(filename: str) -> None:
        with open(filename, 'w') as file:
            file.write("section .data\n")
            file.write("  format_out: db \"%d\", 10, 0\n")
            file.write("  format_in: db \"%d\", 0\n")
            file.write("  scan_int: dd 0\n")
            file.write("\n")
            file.write("section .text\n")
            file.write("  extern printf\n")
            file.write("  extern scanf\n")
            file.write("  global _start\n")
            file.write("\n")
            file.write("_start:\n")
            file.write("  push ebp\n")
            file.write("  mov ebp, esp\n")
            file.write("\n")
            file.write("\n".join(Code.instructions))
            file.write("\n")
            file.write("  mov esp, ebp\n")
            file.write("  pop ebp\n")
            file.write("  mov eax, 1\n")
            file.write("  xor ebx, ebx\n")
            file.write("  int 0x80\n")

class Token():
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

class Variable:
    def __init__(self, value, v_type, shift=None, is_function=False):
        self.value = value
        self.type = v_type
        self.shift = shift
        self.is_function = is_function

class SymbolTable:
    def __init__(self, parent=None):
        self._table = {}
        self.current_shift = 4
        self.parent = parent

    def create_variable(self, name: str, v_type: str, value=None, is_function=False):
        if name in self._table:
            raise Exception(f"[Semantic] Variável já declarada: {name}")

        if value is None and not is_function:
            if v_type == "number":
                value = 0
            elif v_type == "text":
                value = ""
            elif v_type == "boolean":
                value = False
            elif v_type == "array":
                value = []
            elif v_type == "void":
                value = None
            else:
                raise Exception(f"[Semantic] Tipo desconhecido na declaração: {v_type}")

        shift = self.current_shift
        self.current_shift += 4
        self._table[name] = Variable(value, v_type, shift, is_function=is_function)

    def set(self, name: str, value: Variable):
        tbl = self
        while tbl is not None:
            if name in tbl._table:
                target = tbl._table[name]
                if target.is_function:
                    raise Exception(f"[Semantic] Não é possível atribuir a função {name}")
                if target.type != value.type:
                    raise Exception(f"[Semantic] Tipo incompatível para variável {name}: esperado {target.type}, obtido {value.type}")
                target.value = value.value
                return
            tbl = tbl.parent
        raise Exception(f"[Semantic] Variável não declarada: {name}")

    def get(self, name: str) -> Variable:
        tbl = self
        while tbl is not None:
            if name in tbl._table:
                return tbl._table[name]
            tbl = tbl.parent
        raise Exception(f"[Semantic] Variável não declarada: {name}")

class Node():
    id_counter = 0
    @staticmethod
    def newId():
        Node.id_counter += 1
        return Node.id_counter
    def __init__(self, value):
        self.value = value
        self.children = []
        self.id = Node.newId()
    def evaluate(self, st): pass
    def generate(self, st): pass

class ReturnException(Exception):
    def __init__(self, var: Variable):
        self.var = var

class BinOp(Node):
    def __init__(self, value, left, right):
        super().__init__(value)
        self.children = [left, right]
    def evaluate(self, st):
        left_var = self.children[0].evaluate(st)
        right_var = self.children[1].evaluate(st)
        if not isinstance(left_var, Variable) or not isinstance(right_var, Variable):
            raise Exception("[Semantic] Operandos inválidos")
        if self.value in ("+", "-", "*", "/"):
            if left_var.type != "number" or right_var.type != "number":
                raise Exception(f"[Semantic] Operação {self.value} requer números")
            if self.value == "+":
                return Variable(left_var.value + right_var.value, "number")
            elif self.value == "-":
                return Variable(left_var.value - right_var.value, "number")
            elif self.value == "*":
                return Variable(left_var.value * right_var.value, "number")
            elif self.value == "/":
                if right_var.value == 0:
                    raise Exception("[Semantic] Divisão por zero")
                return Variable(left_var.value // right_var.value, "number")
        elif self.value in ("==", "!=", "<", ">", "<=", ">="):
            if left_var.type != right_var.type:
                raise Exception(f"[Semantic] Operação {self.value} requer tipos iguais")
            if self.value == "==":
                return Variable(left_var.value == right_var.value, "boolean")
            elif self.value == "!=":
                return Variable(left_var.value != right_var.value, "boolean")
            elif self.value == "<":
                return Variable(left_var.value < right_var.value, "boolean")
            elif self.value == ">":
                return Variable(left_var.value > right_var.value, "boolean")
            elif self.value == "<=":
                return Variable(left_var.value <= right_var.value, "boolean")
            elif self.value == ">=":
                return Variable(left_var.value >= right_var.value, "boolean")
        elif self.value == "&&":
            if left_var.type != "boolean" or right_var.type != "boolean":
                raise Exception(f"[Semantic] Operação AND requer booleanos")
            return Variable(left_var.value and right_var.value, "boolean")
        elif self.value == "||":
            if left_var.type != "boolean" or right_var.type != "boolean":
                raise Exception(f"[Semantic] Operação OR requer booleanos")
            return Variable(left_var.value or right_var.value, "boolean")
        else:
            raise Exception(f"[Semantic] Operador binário desconhecido: {self.value}")

class UnOp(Node):
    def __init__(self, value, filho):
        super().__init__(value)
        self.children = [filho]
    def evaluate(self, st):
        var = self.children[0].evaluate(st)
        if not isinstance(var, Variable):
            raise Exception("[Semantic] Operando inválido no unário")
        if self.value == "-":
            if var.type != "number":
                raise Exception(f"[Semantic] Operador '-' requer número")
            return Variable(-var.value, "number")
        elif self.value == "!":
            if var.type != "boolean":
                raise Exception(f"[Semantic] Operador '!' requer booleano")
            return Variable(not var.value, "boolean")
        return var

class NumberVal(Node):
    def __init__(self, value):
        super().__init__(value)
    def evaluate(self, st):
        return Variable(self.value, "number")

class BooleanVal(Node):
    def __init__(self, value):
        super().__init__(value)
    def evaluate(self, st):
        return Variable(bool(self.value), "boolean")

class StringVal(Node):
    def __init__(self, value):
        super().__init__(value)
    def evaluate(self, st):
        return Variable(self.value, "text")

class Identifier(Node):
    def __init__(self, name):
        super().__init__(name)
        self.name = name
    def evaluate(self, st):
        return st.get(self.name)

class Assignment(Node):
    def __init__(self, left_identifier, right_expr):
        super().__init__("=")
        self.children = [left_identifier, right_expr]
    def evaluate(self, st):
        if not isinstance(self.children[0], Identifier):
            raise Exception("[Semantic] Lado esquerdo da atribuição deve ser um identificador")
        name = self.children[0].name
        value_var = self.children[1].evaluate(st)
        if not isinstance(value_var, Variable):
            raise Exception("[Semantic] Atribuição com valor inválido")
        st.set(name, value_var)

class VarDec(Node):
    def __init__(self, v_type, identifier, expr=None):
        super().__init__(v_type)
        self.children = [identifier]
        if expr is not None:
            self.children.append(expr)
    def evaluate(self, st):
        name = self.children[0].name
        if self.value is None:
            raise Exception(f"[Semantic] Tipo não especificado na declaração de {name}")
        if len(self.children) == 2:
            value_var = self.children[1].evaluate(st)
            if not isinstance(value_var, Variable):
                raise Exception("[Semantic] Inicializador inválido")
            if self.value != value_var.type:
                raise Exception(f"[Semantic] Tipo incompatível na declaração de {name}: esperado {self.value}, obtido {value_var.type}")
            st.create_variable(name, self.value, value_var.value, is_function=False)
        else:
            st.create_variable(name, self.value, is_function=False)

class Block(Node):
    def __init__(self, children=None):
        super().__init__("block")
        # permite inicializar com uma lista de filhos ou criar vazia
        if children is None:
            self.children = []
        else:
            # fazer uma cópia defensiva para evitar aliasing inesperado
            self.children = list(children)

    def evaluate(self, st):
        for c in self.children:
            # se o filho for um bloco (escopo), criamos uma tabela encadeada
            if isinstance(c, Block):
                new_st = SymbolTable(parent=st)
                try:
                    c.evaluate(new_st)
                except ReturnException:
                    # propaga o return para o chamador
                    raise
            else:
                try:
                    c.evaluate(st)
                except ReturnException:
                    raise
        return None


class NoOp(Node):
    def __init__(self):
        super().__init__("noop")
        self.children = []
    def evaluate(self, st):
        return None

class If(Node):
    def __init__(self, cond, then_branch, else_branch=None):
        super().__init__("if")
        self.children = [cond, then_branch]
        if else_branch is not None:
            self.children.append(else_branch)
    def evaluate(self, st):
        cond_var = self.children[0].evaluate(st)
        if not isinstance(cond_var, Variable) or cond_var.type != "boolean":
            raise Exception("[Semantic] Condição do if deve ser booleana")
        if cond_var.value:
            try:
                return self.children[1].evaluate(st)
            except ReturnException:
                raise
        elif len(self.children) == 3:
            try:
                return self.children[2].evaluate(st)
            except ReturnException:
                raise
        return None

class Until(Node):
    def __init__(self, cond, body):
        super().__init__("until")
        self.children = [cond, body]
    def evaluate(self, st):
        while True:
            cond_var = self.children[0].evaluate(st)
            if not isinstance(cond_var, Variable) or cond_var.type != "boolean":
                raise Exception("[Semantic] Condição do until deve ser booleana")
            if not cond_var.value:
                break
            try:
                self.children[1].evaluate(st)
            except ReturnException:
                raise
        return None

class Return(Node):
    def __init__(self, expr=None):
        super().__init__("return")
        self.children = []
        if expr is not None:
            self.children.append(expr)
    def evaluate(self, st):
        if len(self.children) == 0:
            raise ReturnException(Variable(None, "void"))
        val = self.children[0].evaluate(st)
        if not isinstance(val, Variable):
            raise Exception("[Semantic] Return com valor inválido")
        raise ReturnException(val)

class FuncDec(Node):
    def __init__(self, name):
        super().__init__("func")
        self.name = name
    def evaluate(self, st):
        ret_type = self.value
        vtype = ret_type if ret_type is not None else "void"
        st.create_variable(self.name, vtype, value=self, is_function=True)

class FuncCall(Node):
    def __init__(self, name, args):
        super().__init__("funccall")
        self.name = name
        self.children = args
    def evaluate(self, st):
        var = st.get(self.name)
        if not isinstance(var, Variable) or not var.is_function:
            raise Exception(f"[Semantic] {self.name} não é uma função ou não foi declarada")
        func_node: FuncDec = var.value
        params = []
        if len(func_node.children) >= 2:
            params = func_node.children[1:-1]
        if len(params) != len(self.children):
            raise Exception(f"[Semantic] Chamada a {self.name} com número incorreto de argumentos")
        new_st = SymbolTable(parent=st)
        for i, p in enumerate(params):
            pname = p.children[0].name
            ptype = p.value
            argvar = self.children[i].evaluate(st)
            if not isinstance(argvar, Variable):
                raise Exception("[Semantic] Argumento inválido")
            if argvar.type != ptype:
                raise Exception(f"[Semantic] Tipo de argumento incompatível na chamada de {self.name}")
            new_st.create_variable(pname, ptype, value=argvar.value, is_function=False)
        body_block: Block = func_node.children[-1]
        try:
            body_block.evaluate(new_st)
        except ReturnException as re:
            returned_var = re.var
            if func_node.value is None:
                # função void: aceitar return; e retornar void
                return Variable(None, "void")
            if returned_var.type != func_node.value:
                raise Exception(f"[Semantic] Tipo de retorno incompatível em {self.name}")
            return returned_var
        if func_node.value is None:
            return Variable(None, "void")
        else:
            raise Exception(f"[Semantic] Função {self.name} espera retornar {func_node.value} mas não encontrou return")

class Action(Node):
    def __init__(self, action_type, args):
        super().__init__(action_type)
        self.children = args
    def evaluate(self, st):
        action_type = self.value

        # Avalia um nó (Identifier ou expressão)
        def eval_node(node):
            if isinstance(node, Identifier):
                return node.evaluate(st)
            else:
                return node.evaluate(st)

        # SAY: imprime valor (aceita text ou number)
        if action_type == "say":
            if len(self.children) != 1:
                raise Exception("[Semantic] Ação 'say' requer exatamente 1 argumento")
            arg = eval_node(self.children[0])
            print(arg.value)
            return

        # WAIT: pausa (number)
        if action_type == "wait":
            if len(self.children) != 1:
                raise Exception("[Semantic] Ação 'wait' requer exatamente 1 argumento")
            arg = eval_node(self.children[0])
            if arg.type != "number":
                raise Exception("[Semantic] Ação 'wait' requer number")
            import time
            time.sleep(arg.value)
            return

        # MOVE: apenas narrativa (number)
        if action_type == "move":
            if len(self.children) != 1:
                raise Exception("[Semantic] Ação 'move' requer exatamente 1 argumento")
            arg = eval_node(self.children[0])
            if arg.type != "number":
                raise Exception("[Semantic] Ação 'move' requer number")
            print(f"Movendo {arg.value} unidades")
            return

        # ATTACK: reduz vida de target (identifier) ou de enemy_hp global
        if action_type == "attack":
            # attack() -> decrementa enemy_hp em 1
            if len(self.children) == 0:
                try:
                    target = st.get("enemy_hp")
                except Exception:
                    raise Exception("[Semantic] 'attack()' sem alvo requer variável global 'enemy_hp'")
                if target.type != "number":
                    raise Exception("[Semantic] 'enemy_hp' deve ser number")
                new_val = target.value - 1
                st.set("enemy_hp", Variable(new_val, "number"))
                print(f"Atacado! enemy_hp agora = {new_val}")
                if new_val <= 0:
                    print("Inimigo derrotado!")
                return

            # attack(target) -> decrementa target em 1 (target deve ser Identifier)
            if len(self.children) == 1:
                targ_node = self.children[0]
                if not isinstance(targ_node, Identifier):
                    raise Exception("[Semantic] attack(target) requer Identifier como primeiro argumento")
                targ_var = targ_node.evaluate(st)
                if targ_var.type != "number":
                    raise Exception("[Semantic] target deve ser number")
                new_val = targ_var.value - 1
                st.set(targ_node.name, Variable(new_val, "number"))
                print(f"Atacado! {targ_node.name} agora = {new_val}")
                if new_val <= 0:
                    print("Inimigo derrotado!")
                return

            # attack(target, damage) -> decrementa target por damage
            if len(self.children) == 2:
                targ_node = self.children[0]
                dmg_node = self.children[1]
                if not isinstance(targ_node, Identifier):
                    raise Exception("[Semantic] Primeiro argumento de attack deve ser Identifier")
                targ_var = targ_node.evaluate(st)
                dmg_var = eval_node(dmg_node)
                if targ_var.type != "number" or dmg_var.type != "number":
                    raise Exception("[Semantic] attack(target,damage) requer números")
                new_val = targ_var.value - dmg_var.value
                st.set(targ_node.name, Variable(new_val, "number"))
                print(f"Atacado com {dmg_var.value}! {targ_node.name} agora = {new_val}")
                if new_val <= 0:
                    print("Inimigo derrotado!")
                return

            raise Exception("[Semantic] attack aceita 0, 1 ou 2 argumentos")

        # GATHER: adiciona item ao inventory (se existir), aceita Identifier ou string
        if action_type == "gather":
            if len(self.children) != 1:
                raise Exception("[Semantic] gather espera 1 argumento")
            arg_node = self.children[0]
            if isinstance(arg_node, Identifier):
                item_name = arg_node.name
            else:
                item_var = eval_node(arg_node)
                if item_var.type == "text":
                    item_name = item_var.value
                else:
                    item_name = str(item_var.value)

            # tenta adicionar em inventory se existir
            try:
                inv = st.get("inventory")
                if inv.type != "array":
                    raise Exception("[Semantic] 'inventory' deve ser array se existir")
                new_list = list(inv.value)
                new_list.append(item_name)
                st.set("inventory", Variable(new_list, "array"))
                print(f"Item '{item_name}' adicionado ao inventory")
            except Exception:
                # se não existe inventory, apenas printa
                print(f"Item coletado: {item_name}")
            return

        # USE: usar item — comportamento especial para 'potion'
        if action_type == "use":
            if len(self.children) != 1:
                raise Exception("[Semantic] use espera 1 argumento")
            arg_node = self.children[0]
            # resolve nome do item
            if isinstance(arg_node, Identifier):
                item_name = arg_node.name
            else:
                item_var = eval_node(arg_node)
                item_name = item_var.value

            # Se for 'potion' (string), cura o player (health) usando potion_heal se existir
            if str(item_name) == "potion":
                try:
                    health_var = st.get("health")
                except Exception:
                    raise Exception("[Semantic] Variável 'health' não encontrada para usar potion")
                if health_var.type != "number":
                    raise Exception("[Semantic] 'health' deve ser number")

                # procurar potion_heal na tabela; se não existir, usar 50
                try:
                    potion_heal_var = st.get("potion_heal")
                    if potion_heal_var.type != "number":
                        heal_amount = 50
                    else:
                        heal_amount = potion_heal_var.value
                except Exception:
                    heal_amount = 50

                # checar max_health se houver
                try:
                    max_h = st.get("max_health")
                    if max_h.type == "number":
                        cap = max_h.value
                    else:
                        cap = health_var.value + heal_amount
                except Exception:
                    cap = health_var.value + heal_amount

                new_health = min(health_var.value + heal_amount, cap)
                st.set("health", Variable(new_health, "number"))

                # remover potion do inventory se presente
                try:
                    inv = st.get("inventory")
                    if inv.type == "array":
                        new_list = list(inv.value)
                        if "potion" in new_list:
                            new_list.remove("potion")
                            st.set("inventory", Variable(new_list, "array"))
                except Exception:
                    pass

                print(f"Você usou uma potion. Vida agora = {new_health}")
                return
            else:
                # comportamento genérico: apenas print
                print(f"Usando {item_name}")
                return

        raise Exception(f"[Semantic] Ação desconhecida: {action_type}")



class ArrayAccess(Node):
    def __init__(self, identifier, index):
        super().__init__("array_access")
        self.children = [identifier, index]

    def evaluate(self, st):
        # Primeiro avalia a referência ao array
        array_var = self.children[0].evaluate(st)
        if not isinstance(array_var, Variable):
            raise Exception("[Semantic] Acesso a array: operando esquerdo não é variável")
        if array_var.type != "array":
            raise Exception("[Semantic] Tentativa de acessar não-array")
        # Avalia o índice
        index_var = self.children[1].evaluate(st)
        if not isinstance(index_var, Variable):
            raise Exception("[Semantic] Índice inválido no acesso a array")
        if index_var.type != "number":
            raise Exception("[Semantic] Índice de array deve ser number")
        idx = index_var.value
        if idx < 0 or idx >= len(array_var.value):
            raise Exception("[Semantic] Índice fora do intervalo")
        elem = array_var.value[idx]

        # Converte o elemento Python em Variable com tipo apropriado
        if isinstance(elem, bool):
            return Variable(elem, "boolean")
        elif isinstance(elem, int):
            return Variable(elem, "number")
        elif isinstance(elem, str):
            return Variable(elem, "text")
        elif isinstance(elem, list):
            return Variable(list(elem), "array")
        else:
            # fallback: stringify
            return Variable(elem, "text")


class ArrayLiteral(Node):
    def __init__(self, elements):
        super().__init__("array_literal")
        self.children = elements
    def evaluate(self, st):
        evaluated_elements = []
        for element in self.children:
            eval_element = element.evaluate(st)
            evaluated_elements.append(eval_element.value)
        return Variable(evaluated_elements, "array")

class LenCall(Node):
    def __init__(self, identifier):
        super().__init__("len")
        self.children = [identifier]
    def evaluate(self, st):
        array_var = self.children[0].evaluate(st)
        if array_var.type != "array":
            raise Exception("[Semantic] 'len' só pode ser aplicado a arrays")
        return Variable(len(array_var.value), "number")

class Prepro:
    def filter(code: str) -> str:
        code = re.sub(r'//[^\n]*', '', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

class Lexer():
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.next = None
        self.selectNext()
    def selectNext(self):
        while self.position < len(self.source) and self.source[self.position] in ' \t\r\n':
            self.position += 1
        if self.position >= len(self.source):
            self.next = Token("EOF", "")
            return
        c_atual = self.source[self.position]
        if c_atual.isalpha() or c_atual == '_':
            ident = ''
            while self.position < len(self.source) and (self.source[self.position].isalnum() or self.source[self.position] == '_'):
                ident += self.source[self.position]
                self.position += 1
            keywords = {
                "text": "TEXT_TYPE", "number": "NUMBER_TYPE", "boolean": "BOOLEAN_TYPE",
                "array": "ARRAY_TYPE", "func": "FUNC", "entity": "ENTITY", "if": "IF",
                "else": "ELSE", "until": "UNTIL", "during": "DURING", "return": "RETURN",
                "move": "MOVE", "attack": "ATTACK", "gather": "GATHER", "use": "USE",
                "say": "SAY", "wait": "WAIT", "true": "TRUE", "false": "FALSE", "len": "LEN"
            }
            if ident in keywords:
                self.next = Token(keywords[ident], ident)
            else:
                self.next = Token("IDENTIFIER", ident)
            return
        elif c_atual.isdigit():
            num = ''
            while self.position < len(self.source) and self.source[self.position].isdigit():
                num += self.source[self.position]
                self.position += 1
            self.next = Token("NUMBER", int(num))
            return
        elif c_atual == '"':
            string_val = ''
            self.position += 1
            while self.position < len(self.source) and self.source[self.position] != '"':
                string_val += self.source[self.position]
                self.position += 1
            if self.position >= len(self.source) or self.source[self.position] != '"':
                raise Exception("String não fechada")
            self.position += 1
            self.next = Token("STRING", string_val)
            return
        elif c_atual == '&' and self.position + 1 < len(self.source) and self.source[self.position + 1] == '&':
            self.next = Token("AND", "&&"); self.position += 2
        elif c_atual == '|' and self.position + 1 < len(self.source) and self.source[self.position + 1] == '|':
            self.next = Token("OR", "||"); self.position += 2
        elif c_atual == '=' and self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
            self.next = Token("EQ", "=="); self.position += 2
        elif c_atual == '!' and self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
            self.next = Token("NE", "!="); self.position += 2
        elif c_atual == '<' and self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
            self.next = Token("LE", "<="); self.position += 2
        elif c_atual == '>' and self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
            self.next = Token("GE", ">="); self.position += 2
        elif c_atual == '<':
            self.next = Token("LT", "<"); self.position += 1
        elif c_atual == '>':
            self.next = Token("GT", ">"); self.position += 1
        elif c_atual == '=':
            self.next = Token("ASSIGN", "="); self.position += 1
        elif c_atual == '+':
            self.next = Token("PLUS", "+"); self.position += 1
        elif c_atual == '-':
            self.next = Token("MINUS", "-"); self.position += 1
        elif c_atual == '*':
            self.next = Token("TIMES", "*"); self.position += 1
        elif c_atual == '/':
            self.next = Token("DIVIDE", "/"); self.position += 1
        elif c_atual == '(':
            self.next = Token("LPAREN", "("); self.position += 1
        elif c_atual == ')':
            self.next = Token("RPAREN", ")"); self.position += 1
        elif c_atual == '{':
            self.next = Token("LBRACE", "{"); self.position += 1
        elif c_atual == '}':
            self.next = Token("RBRACE", "}"); self.position += 1
        elif c_atual == '[':
            self.next = Token("LBRACKET", "["); self.position += 1
        elif c_atual == ']':
            self.next = Token("RBRACKET", "]"); self.position += 1
        elif c_atual == ':':
            self.next = Token("COLON", ":"); self.position += 1
        elif c_atual == ';':
            self.next = Token("SEMICOLON", ";"); self.position += 1
        elif c_atual == ',':
            self.next = Token("COMMA", ","); self.position += 1
        else:
            raise Exception(f"Caractere inválido: {c_atual}")

class Parser():
    def __init__(self, lexer):
        self.lexer = lexer
    def _err(self, msg):
        raise Exception(f"[Parser] {msg}")

    # ---------- MODIFICADO: aceita IDENTIFIER: ... como declaração no topo ----------
    def parseProgram(self):
        declarations = []
        while self.lexer.next.kind != "EOF":
            # detecta declaração de variável iniciada por IDENTIFIER :
            if self.lexer.next.kind == "IDENTIFIER":
                saved_pos = self.lexer.position
                saved_next = self.lexer.next
                self.lexer.selectNext()
                next_kind = self.lexer.next.kind
                # restaura
                self.lexer.position = saved_pos
                self.lexer.next = saved_next
                if next_kind == "COLON":
                    declarations.append(self.parseVariableDeclaration())
                    continue
            if self.lexer.next.kind == "FUNC":
                declarations.append(self.parseFuncDeclaration())
            elif self.lexer.next.kind == "ENTITY":
                declarations.append(self.parseEntityDeclaration())
            else:
                declarations.append(self.parseCommand())
        return Block(declarations)

    def parseVariableDeclaration(self):
        if self.lexer.next.kind != "IDENTIFIER":
            self._err("Esperado identificador")
        identifier = Identifier(self.lexer.next.value)
        self.lexer.selectNext()
        if self.lexer.next.kind != "COLON":
            self._err("Esperado ':'")
        self.lexer.selectNext()
        if self.lexer.next.kind not in ["TEXT_TYPE", "NUMBER_TYPE", "BOOLEAN_TYPE", "ARRAY_TYPE"]:
            self._err("Esperado tipo")
        var_type = self.lexer.next.value
        self.lexer.selectNext()
        if self.lexer.next.kind != "ASSIGN":
            self._err("Esperado '='")
        self.lexer.selectNext()
        expr = self.parseExpression()
        if self.lexer.next.kind != "SEMICOLON":
            self._err("Esperado ';'")
        self.lexer.selectNext()
        return VarDec(var_type, identifier, expr)

    def parseFuncDeclaration(self):
        if self.lexer.next.kind != "FUNC":
            self._err("Esperado 'func'")
        self.lexer.selectNext()
        if self.lexer.next.kind != "IDENTIFIER":
            self._err("Esperado identificador")
        func_name = self.lexer.next.value
        self.lexer.selectNext()
        if self.lexer.next.kind != "LPAREN":
            self._err("Esperado '('")
        self.lexer.selectNext()
        params = []
        if self.lexer.next.kind != "RPAREN":
            while True:
                if self.lexer.next.kind != "IDENTIFIER":
                    self._err("Esperado identificador de parâmetro")
                param_name = self.lexer.next.value
                self.lexer.selectNext()
                if self.lexer.next.kind != "COLON":
                    self._err("Esperado ':'")
                self.lexer.selectNext()
                if self.lexer.next.kind not in ["TEXT_TYPE", "NUMBER_TYPE", "BOOLEAN_TYPE", "ARRAY_TYPE"]:
                    self._err("Esperado tipo")
                param_type = self.lexer.next.value
                self.lexer.selectNext()
                params.append(VarDec(param_type, Identifier(param_name)))
                if self.lexer.next.kind == "COMMA":
                    self.lexer.selectNext()
                    continue
                else:
                    break
        if self.lexer.next.kind != "RPAREN":
            self._err("Esperado ')'")
        self.lexer.selectNext()
        return_type = None
        if self.lexer.next.kind == "COLON":
            self.lexer.selectNext()
            if self.lexer.next.kind not in ["TEXT_TYPE", "NUMBER_TYPE", "BOOLEAN_TYPE", "ARRAY_TYPE"]:
                self._err("Esperado tipo de retorno")
            return_type = self.lexer.next.value
            self.lexer.selectNext()
        if self.lexer.next.kind != "LBRACE":
            self._err("Esperado '{'")
        body = self.parseBlock()
        func_node = FuncDec(func_name)
        func_node.value = return_type
        func_node.children.append(Identifier(func_name))
        for p in params:
            func_node.children.append(p)
        func_node.children.append(body)
        return func_node

    # ---------- MODIFICADO: aceita IDENTIFIER: ... como membro de entity ----------
    def parseEntityDeclaration(self):
        if self.lexer.next.kind != "ENTITY":
            self._err("Esperado 'entity'")
        self.lexer.selectNext()
        if self.lexer.next.kind != "IDENTIFIER":
            self._err("Esperado identificador")
        entity_name = self.lexer.next.value
        self.lexer.selectNext()
        if self.lexer.next.kind != "LBRACE":
            self._err("Esperado '{'")
        self.lexer.selectNext()
        members = []
        while self.lexer.next.kind != "RBRACE" and self.lexer.next.kind != "EOF":
            if self.lexer.next.kind == "IDENTIFIER":
                saved_pos = self.lexer.position
                saved_next = self.lexer.next
                self.lexer.selectNext()
                next_kind = self.lexer.next.kind
                self.lexer.position = saved_pos
                self.lexer.next = saved_next
                if next_kind == "COLON":
                    members.append(self.parseVariableDeclaration())
                    continue
                else:
                    self._err("Membro de entidade inválido: esperado ':' após identificador")
            elif self.lexer.next.kind == "FUNC":
                members.append(self.parseFuncDeclaration())
                continue
            else:
                self._err("Membro de entidade inválido")
        if self.lexer.next.kind != "RBRACE":
            self._err("Esperado '}'")
        self.lexer.selectNext()
        entity_block = Block()
        entity_block.children = members
        return entity_block

    def parseCommand(self):
        # aceitar ';' solto como NoOp (declaração vazia)
        if self.lexer.next.kind == "SEMICOLON":
            self.lexer.selectNext()
            return NoOp()

        # Se for uma possível declaração local: IDENTIFIER :
        if self.lexer.next.kind == "IDENTIFIER":
            # lookahead: salva estado, avança e verifica se vem COLON
            saved_pos = self.lexer.position
            saved_next = self.lexer.next
            self.lexer.selectNext()
            next_kind = self.lexer.next.kind
            # restaura estado
            self.lexer.position = saved_pos
            self.lexer.next = saved_next

            if next_kind == "COLON":
                # declaração local dentro de bloco/função
                return self.parseVariableDeclaration()

        # blocos, if, until, return, actions
        if self.lexer.next.kind == "LBRACE":
            return self.parseBlock()
        elif self.lexer.next.kind == "IF":
            return self.parseIf()
        elif self.lexer.next.kind == "UNTIL":
            return self.parseUntil()
        elif self.lexer.next.kind == "RETURN":
            return self.parseReturn()
        elif self.lexer.next.kind in ["MOVE", "ATTACK", "GATHER", "USE", "SAY", "WAIT"]:
            return self.parseAction()

        # identificador pode ser chamada de função ou atribuição (ou array assign)
        if self.lexer.next.kind == "IDENTIFIER":
            lookahead = self.lexer.next.value
            # consume identifier
            self.lexer.selectNext()

            # chamada de função abre parênteses: ident(...)
            if self.lexer.next.kind == "LPAREN":
                node = self.parseFuncCall(lookahead)
                # função chamada como statement deve terminar com ';'
                if self.lexer.next.kind == "SEMICOLON":
                    self.lexer.selectNext()
                    return node
                else:
                    self._err("Esperado ';' após chamada de função")

            # chamada de função *sem parênteses* e seguida por ';' -> tratamos como ident()
            if self.lexer.next.kind == "SEMICOLON":
                # interpretamos "ident;" como "ident();" (chamada sem args)
                self.lexer.selectNext()
                return FuncCall(lookahead, [])

            # assignment normal: ident = expr ;
            if self.lexer.next.kind == "ASSIGN":
                return self.parseAssignment(lookahead)

            # atribuição em array: ident [ expr ] = expr ;
            if self.lexer.next.kind == "LBRACKET":
                return self.parseArrayAssignment(lookahead)

            self._err(f"Comando inválido: token após identificador = {self.lexer.next.kind}")

        # qualquer outro token inválido para começo de comando
        self._err(f"Comando inválido: {self.lexer.next.kind}")




    def parseBlock(self):
        if self.lexer.next.kind != "LBRACE":
            self._err("Esperado '{'")
        self.lexer.selectNext()

        commands = []
        # aceitar vários ';' soltos dentro do bloco e pular
        while self.lexer.next.kind != "RBRACE" and self.lexer.next.kind != "EOF":
            # pular ';' vazios (NoOp)
            if self.lexer.next.kind == "SEMICOLON":
                self.lexer.selectNext()
                continue
            commands.append(self.parseCommand())

        if self.lexer.next.kind != "RBRACE":
            self._err("Esperado '}'")
        self.lexer.selectNext()

        block = Block()
        block.children = commands
        return block


    def parseIf(self):
        if self.lexer.next.kind != "IF":
            self._err("Esperado 'if'")
        self.lexer.selectNext()
        if self.lexer.next.kind != "LPAREN":
            self._err("Esperado '('")
        self.lexer.selectNext()
        cond = self.parseExpression()
        if self.lexer.next.kind != "RPAREN":
            self._err("Esperado ')'")
        self.lexer.selectNext()
        then_branch = self.parseCommand()
        else_branch = None
        if self.lexer.next.kind == "ELSE":
            self.lexer.selectNext()
            else_branch = self.parseCommand()
        return If(cond, then_branch, else_branch)

    def parseUntil(self):
        if self.lexer.next.kind != "UNTIL":
            self._err("Esperado 'until'")
        self.lexer.selectNext()
        if self.lexer.next.kind != "LPAREN":
            self._err("Esperado '('")
        self.lexer.selectNext()
        cond = self.parseExpression()
        if self.lexer.next.kind != "RPAREN":
            self._err("Esperado ')'")
        self.lexer.selectNext()
        body = self.parseCommand()
        return Until(cond, body)

    # ---------- MODIFICADO: aceita return; (sem expressão) ----------
    def parseReturn(self):
        if self.lexer.next.kind != "RETURN":
            self._err("Esperado 'return'")
        self.lexer.selectNext()
        if self.lexer.next.kind == "SEMICOLON":
            self.lexer.selectNext()
            return Return(None)
        expr = self.parseExpression()
        if self.lexer.next.kind != "SEMICOLON":
            self._err("Esperado ';'")
        self.lexer.selectNext()
        return Return(expr)

    def parseAction(self):
        action_type = self.lexer.next.kind.lower()
        self.lexer.selectNext()
        if self.lexer.next.kind != "LPAREN":
            self._err("Esperado '('")
        self.lexer.selectNext()
        args = []
        if self.lexer.next.kind != "RPAREN":
            args.append(self.parseExpression())
            while self.lexer.next.kind == "COMMA":
                self.lexer.selectNext()
                args.append(self.parseExpression())
        if self.lexer.next.kind != "RPAREN":
            self._err("Esperado ')'")
        self.lexer.selectNext()
        if self.lexer.next.kind != "SEMICOLON":
            self._err("Esperado ';'")
        self.lexer.selectNext()
        return Action(action_type, args)

    def parseAssignment(self, identifier):
        if self.lexer.next.kind != "ASSIGN":
            self._err("Esperado '='")
        self.lexer.selectNext()
        expr = self.parseExpression()
        if self.lexer.next.kind != "SEMICOLON":
            self._err("Esperado ';'")
        self.lexer.selectNext()
        return Assignment(Identifier(identifier), expr)

    def parseArrayAssignment(self, identifier):
        if self.lexer.next.kind != "LBRACKET":
            self._err("Esperado '['")
        self.lexer.selectNext()
        index = self.parseExpression()
        if self.lexer.next.kind != "RBRACKET":
            self._err("Esperado ']'")
        self.lexer.selectNext()
        if self.lexer.next.kind != "ASSIGN":
            self._err("Esperado '='")
        self.lexer.selectNext()
        expr = self.parseExpression()
        if self.lexer.next.kind != "SEMICOLON":
            self._err("Esperado ';'")
        self.lexer.selectNext()
        return Assignment(Identifier(identifier), expr)

    def parseExpression(self):
        return self.parseLogicalExpression()

    def parseLogicalExpression(self):
        node = self.parseRelationalExpression()
        while self.lexer.next.kind in ["AND", "OR"]:
            op = self.lexer.next.value
            self.lexer.selectNext()
            right = self.parseRelationalExpression()
            node = BinOp(op, node, right)
        return node

    def parseRelationalExpression(self):
        node = self.parseArithmeticExpression()
        while self.lexer.next.kind in ["EQ", "NE", "LT", "GT", "LE", "GE"]:
            op = self.lexer.next.value
            self.lexer.selectNext()
            right = self.parseArithmeticExpression()
            node = BinOp(op, node, right)
        return node

    def parseArithmeticExpression(self):
        node = self.parseTerm()
        while self.lexer.next.kind in ["PLUS", "MINUS"]:
            op = self.lexer.next.value
            self.lexer.selectNext()
            right = self.parseTerm()
            node = BinOp(op, node, right)
        return node

    def parseTerm(self):
        node = self.parseFactor()
        while self.lexer.next.kind in ["TIMES", "DIVIDE"]:
            op = self.lexer.next.value
            self.lexer.selectNext()
            right = self.parseFactor()
            node = BinOp(op, node, right)
        return node

    def parseFactor(self):
        if self.lexer.next.kind in ["PLUS", "MINUS", "NOT"]:
            op = self.lexer.next.value
            self.lexer.selectNext()
            child = self.parseFactor()
            return UnOp(op, child)
        elif self.lexer.next.kind == "NUMBER":
            val = self.lexer.next.value
            self.lexer.selectNext()
            return NumberVal(val)
        elif self.lexer.next.kind == "TRUE":
            self.lexer.selectNext()
            return BooleanVal(True)
        elif self.lexer.next.kind == "FALSE":
            self.lexer.selectNext()
            return BooleanVal(False)
        elif self.lexer.next.kind == "STRING":
            val = self.lexer.next.value
            self.lexer.selectNext()
            return StringVal(val)
        elif self.lexer.next.kind == "LPAREN":
            self.lexer.selectNext()
            node = self.parseExpression()
            if self.lexer.next.kind != "RPAREN":
                self._err("Esperado ')'")
            self.lexer.selectNext()
            return node
        elif self.lexer.next.kind == "LBRACKET":
            return self.parseArrayLiteral()
        elif self.lexer.next.kind == "IDENTIFIER":
            identifier = self.lexer.next.value
            self.lexer.selectNext()
            if self.lexer.next.kind == "LPAREN":
                return self.parseFuncCall(identifier)
            elif self.lexer.next.kind == "LBRACKET":
                return self.parseArrayAccess(identifier)
            else:
                return Identifier(identifier)
        elif self.lexer.next.kind == "LEN":
            return self.parseLenCall()
        else:
            self._err(f"Fator inválido: {self.lexer.next.kind}")

    def parseArrayLiteral(self):
        if self.lexer.next.kind != "LBRACKET":
            self._err("Esperado '['")
        self.lexer.selectNext()
        elements = []
        if self.lexer.next.kind != "RBRACKET":
            elements.append(self.parseExpression())
            while self.lexer.next.kind == "COMMA":
                self.lexer.selectNext()
                elements.append(self.parseExpression())
        if self.lexer.next.kind != "RBRACKET":
            self._err("Esperado ']'")
        self.lexer.selectNext()
        return ArrayLiteral(elements)

    def parseFuncCall(self, identifier):
        if self.lexer.next.kind != "LPAREN":
            self._err("Esperado '('")
        self.lexer.selectNext()
        args = []
        if self.lexer.next.kind != "RPAREN":
            args.append(self.parseExpression())
            while self.lexer.next.kind == "COMMA":
                self.lexer.selectNext()
                args.append(self.parseExpression())
        if self.lexer.next.kind != "RPAREN":
            self._err("Esperado ')'")
        self.lexer.selectNext()
        return FuncCall(identifier, args)

    def parseArrayAccess(self, identifier):
        if self.lexer.next.kind != "LBRACKET":
            self._err("Esperado '['")
        self.lexer.selectNext()
        index = self.parseExpression()
        if self.lexer.next.kind != "RBRACKET":
            self._err("Esperado ']'")
        self.lexer.selectNext()
        return ArrayAccess(Identifier(identifier), index)

    def parseLenCall(self):
        if self.lexer.next.kind != "LEN":
            self._err("Esperado 'len'")
        self.lexer.selectNext()
        if self.lexer.next.kind != "LPAREN":
            self._err("Esperado '('")
        self.lexer.selectNext()
        if self.lexer.next.kind != "IDENTIFIER":
            self._err("Esperado identificador")
        identifier = self.lexer.next.value
        self.lexer.selectNext()
        if self.lexer.next.kind != "RPAREN":
            self._err("Esperado ')'")
        self.lexer.selectNext()
        return LenCall(Identifier(identifier))

    def run(self):
        node = self.parseProgram()
        if self.lexer.next.kind != "EOF":
            self._err("Tokens extras após programa")
        return node

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 main.py <arquivo.level>")
        sys.exit(1)
    filename = sys.argv[1]
    try:
        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(f"Erro ao abrir arquivo {filename}: {e}")
        sys.exit(1)
    code = Prepro.filter(code)
    lexer = Lexer(code)
    parser = Parser(lexer)
    try:
        arvore = parser.run()
    except Exception as e:
        print(e)
        sys.exit(1)
    st = SymbolTable()
    try:
        arvore.evaluate(st)
    except Exception as e:
        print(e)
        sys.exit(1)
    try:
        arvore.generate(st)
    except Exception as e:
        print("Erro durante geração de código:", e)
        sys.exit(1)
    outname = os.path.splitext(filename)[0] + ".asm"
    Code.dump(outname)

if __name__ == "__main__":
    main()
