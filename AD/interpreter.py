""" SPI - Simple Pascal Interpreter """
import copy
import math
import unicodedata
###############################################################################
#                                                                             #
#  LEXER                                                                      #
#                                                                             #
###############################################################################

# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
INTEGER, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, EOF, VAR, COS, SIN, EXP,POW, LOG, COMMA = (
    'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', '(', ')', 'EOF', 'VAR', 'COS', 'SIN', 'EXP', 'POW', 'LOG', ','
)


class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        """String representation of the class instance.

        Examples:
            Token(INTEGER, 3)
            Token(PLUS, '+')
            Token(MUL, '*')
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


class Lexer(object):
    def __init__(self, text):
        # client string input, e.g. "4 + 2 * 3 - 6 / 2"
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise NameError('Invalid character')

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            pass

        return False

    def integer(self):
        """Return a (multidigit) integer consumed from the input."""

        index = 0
        while(self.is_number(self.text[self.pos:len(self.text)-index])==False):
            index += 1
        number = self.text[self.pos:len(self.text)-index]
        index = 0
        while(index < len(number)):
          self.advance()
          index += 1
        return float(number)

    def word(self):
        """Return a multichar integer consumed from the input."""
        result = ''
        while self.current_char is not None and self.current_char.isalpha():
            result += self.current_char
            self.advance()
        return  result

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)

        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            if self.current_char.isalpha():
                w = self.word()
                if(w.upper() == "COS"):
                    return Token(COS, self.word())
                elif(w.upper() == "SIN"):
                    return Token(SIN, self.word())
                elif(w.upper() == "EXP"):
                    return Token(EXP, self.word())
                elif(w.upper() == "POW"):
                    return Token(POW, self.word())
                elif(w.upper() == "LOG"):
                    return Token(LOG, self.word())
                else:
                    return Token(VAR, w)

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')

            self.error()

        return Token(EOF, None)


###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################

class AST(object):
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Var(AST):
    def __init__(self, token):
        self.token = token
        self.name = token.value

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise NameError('Invalid syntax')

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        """factor : (PLUS | MINUS) factor | INTEGER | VAR | LPAREN expr RPAREN"""
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        elif token.type == VAR:
            self.eat(VAR)
            return Var(token)
        elif token.type == COS:
            self.eat(COS)
            self.eat(LPAREN)
            x = self.expr()
            node = UnaryOp(token, x)
            self.eat(RPAREN)
            return node
        elif token.type == SIN:
            self.eat(SIN)
            self.eat(LPAREN)
            x = self.expr()
            node = UnaryOp(token, x)
            self.eat(RPAREN)
            return node
        elif token.type == EXP:
            self.eat(EXP)
            self.eat(LPAREN)
            x = self.expr()
            node = UnaryOp(token, x)
            self.eat(RPAREN)
            return node
        elif token.type == POW:
            self.eat(POW)
            self.eat(LPAREN)
            x = self.expr()
            self.eat(COMMA)
            y = self.expr()
            self.eat(RPAREN)
            return BinOp(left = x, op = token, right = y)
        elif token.type == LOG:
            self.eat(LOG)
            self.eat(LPAREN)
            x = self.expr()
            self.eat(RPAREN)
            return UnaryOp(token, x)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node

    def term(self):
        """term : factor ((MUL | DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def expr(self):
        """
        expr   : term ((PLUS | MINUS) term)*
        term   : factor ((MUL | DIV) factor)*
        factor : (PLUS | MINUS) factor | INTEGER | LPAREN expr RPAREN
        """
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def parse(self):
        node = self.expr()
        if self.current_token.type != EOF:
            self.error()
        return node

    def dfactor(self):
        """factor : (PLUS | MINUS) factor | INTEGER | VAR | LPAREN expr RPAREN"""
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.dfactor())
            return node, node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.dfactor())
            return node, node
        elif token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token), Num(Token(INTEGER, 0))
        elif token.type == VAR:
            self.eat(VAR)
            return Var(token), Var(Token(VAR, "d_" + token.value))
        elif token.type == COS:
            self.eat(COS)
            self.eat(LPAREN)
            cur = copy.deepcopy(self)
            x = self.expr()
            dx = cur.dexpr()
            node = UnaryOp(token, x)
            self.eat(RPAREN)
            return node,  BinOp(left = UnaryOp(Token(MINUS, "-"), UnaryOp(Token(SIN, "sin"), x)), op=Token(MUL,'*'), right=dx)
        elif token.type == SIN:
            self.eat(SIN)
            self.eat(LPAREN)
            cur = copy.deepcopy(self)
            x = self.expr()
            dx = cur.dexpr()
            node = UnaryOp(token, x)
            self.eat(RPAREN)
            return node, BinOp(left = UnaryOp(Token(COS, "cos"), x), op=Token(MUL,'*'), right=dx)
        elif token.type == EXP:
            self.eat(EXP)
            self.eat(LPAREN)
            cur = copy.deepcopy(self)
            x = self.expr()
            dx = cur.dexpr()
            node = UnaryOp(token, x)
            self.eat(RPAREN)
            return node, BinOp(left = node, op=Token(MUL,'*'), right=dx)
        elif token.type == POW:
            self.eat(POW)
            self.eat(LPAREN)
            x_cur = copy.deepcopy(self)
            x = self.expr()
            dx = x_cur.dexpr()
            self.eat(COMMA)
            y_cur = copy.deepcopy(self)
            y = self.expr()
            dy = y_cur.dexpr()
            self.eat(RPAREN)
            node = BinOp(left = x, op = token, right = y)
            return node, BinOp(left = node, op = Token(MUL, '*'), right = BinOp(left = BinOp(left = BinOp(left = y, op = Token(DIV,'/'), right = x), op = Token(MUL,'*'), right = dx), op = Token(PLUS, '+'), right = BinOp(left = dy, op = Token(MUL, '*'),right = UnaryOp(Token(LOG, 'LOG'), x))))
        elif token.type == LOG:
            self.eat(LOG)
            self.eat(LPAREN)
            cur = copy.deepcopy(self)
            x = self.expr()
            dx = cur.dexpr()
            node = UnaryOp(token, x)
            self.eat(RPAREN)
            return node, BinOp(left = dx, op=Token(DIV,'/'), right=x)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            cur = copy.deepcopy(self)
            node = self.expr()
            dnode = cur.dexpr()
            self.eat(RPAREN)
            return node, dnode
        else:
            raise NameError('Invalid character')


    def dterm(self):
        """term : factor ((MUL | DIV) factor)*"""
        node, dnode = self.dfactor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)
                
            if self is None:
                raise Exception('Invalid character')
                
            rnode, rdnode = self.dfactor()
            lowdhi = BinOp(left=dnode, op=Token(MUL,'*'), right=rnode)
            hidlow = BinOp(left=node, op=Token(MUL,'*'), right=rdnode)
            if token.type == MUL:
                # chain rule
                dnode = BinOp(left=lowdhi, op=Token(PLUS,'+'), right=hidlow)
                node = BinOp(left=node, op=Token(MUL,'*'), right=rnode)
            else:
                # quotient rule
                topnode = BinOp(left=lowdhi, op=Token(MINUS, '-'), right=hidlow)
                botnode = BinOp(left=rnode, op=Token(MUL,'*'), right=rnode)
                dnode = BinOp(left=topnode, op=Token(DIV,'/'), right=botnode)
                node = BinOp(left=node, op=Token(DIV,'/'), right=rnode)
        return dnode

    def dexpr(self):
        """
        expr   : term ((PLUS | MINUS) term)*
        term   : factor ((MUL | DIV) factor)*
        factor : (PLUS | MINUS) factor | INTEGER | LPAREN expr RPAREN
        """
        dnode = self.dterm()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            dnode = BinOp(left=dnode, op=token, right=self.dterm())
        return dnode


    def dparse(self):
        node = self.dexpr()
        if self.current_token.type != EOF:
            self.error()
        return node

###############################################################################
#                                                                             #
#  INTERPRETER                                                                #
#                                                                             #
###############################################################################

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.dtree = copy.deepcopy(parser).dparse()
        self.tree = copy.deepcopy(parser).parse()

    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) / self.visit(node.right)
        elif node.op.type == POW:
            return math.pow(self.visit(node.left), self.visit(node.right))

    def visit_Num(self, node):
        return node.value

    def visit_Var(self, node):
        if self.vardict is None:
            raise NameError("no var dict passed in")
        if node.name not in self.vardict:
            raise NameError("var {} not in var dict".format(node.name))
        return self.vardict[node.name]

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)
        elif op == COS:
            return math.cos(self.visit(node.expr))
        elif op == SIN:
            return math.sin(self.visit(node.expr))
        elif op == EXP:
            return math.exp(self.visit(node.expr))
        elif op == LOG:
            return math.log(self.visit(node.expr))

    def interpret(self, vd=None):
        self.get_vardict(vd)
        tree = self.tree
        if tree is None:
            return ''
        return self.visit(tree)

    def differentiate(self, vd=None, dv=None):
        self.get_vardict(vd)
        self.get_diffvar(dv)
        tree = self.dtree
        if tree is None:
            return ''
        return self.visit(tree)

    def diff_all(self, vd=None):
        self.get_vardict(vd)
        tree = self.dtree
        if tree is None:
            return ''
        variables = list(self.vardict.keys())
        ret = {}
        for v in variables:
            self.vardict["d_"+v] = 0
        for v in variables:
            self.vardict["d_"+v] = 1
            ret["d_{}".format(v)]=self.visit(tree)
            self.vardict["d_"+v] = 0
        return ret

    def get_vardict(self, vd=None):
        """ expects vardict to be formatted as x:10, y:20, z:3 """
        vdict = {}
        if vd is None:
            text = input('vardict> ')
            if not text:
                self.vardict = None
                return
        else:
            text = vd
        text = text.replace(" ", "")
        for var in text.split(','):
            vals = var.split(':')
            vdict[str(vals[0])] = float(vals[1])
        self.vardict = vdict
        return

    def get_diffvar(self, dv=None):
        if dv is None:
            text = input('d_var> ')
        else:
            text = dv
        text = text.replace(" ", "")
        if text not in self.vardict.keys():
            raise NameError("d_var not in vardict")
        for v in list(self.vardict.keys()):
            self.vardict["d_"+v]=0
        self.vardict["d_"+text]=1
        return



# def main():
    # if run as main, can take inputs from command line
    # while True:
    #     try:
    #         try:
    #             text = raw_input('spi> ')
    #         except NameError:  # Python3
    #             text = input('spi> ')
    #     except EOFError:
    #         break
    #     if not text:
    #         continue

    #     lexer = Lexer(text)
    #     parser = Parser(lexer)
    #     interpreter = Interpreter(parser)
    #     result = interpreter.differentiate()
    #     print(result)

# if __name__ == '__main__':
#     main()

'''
Based off of the open source tutorial: Let's Build a Simple Interpreter
https://github.com/rspivak/lsbasi/tree/master/part8/python
'''
