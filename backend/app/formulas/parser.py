from __future__ import annotations
"""
Formula parser: tokenizer + recursive descent parser → AST.

Supports: arithmetic, comparisons, string concat (&), cell refs, ranges, function calls, nested expressions.
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto


# ── AST Nodes ──

class NodeType(Enum):
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    CELL_REF = auto()
    RANGE_REF = auto()
    BINARY_OP = auto()
    UNARY_OP = auto()
    FUNCTION_CALL = auto()
    ERROR = auto()


@dataclass
class ASTNode:
    node_type: NodeType


@dataclass
class NumberNode(ASTNode):
    value: float
    node_type: NodeType = field(default=NodeType.NUMBER, init=False)


@dataclass
class StringNode(ASTNode):
    value: str
    node_type: NodeType = field(default=NodeType.STRING, init=False)


@dataclass
class BooleanNode(ASTNode):
    value: bool
    node_type: NodeType = field(default=NodeType.BOOLEAN, init=False)


@dataclass
class CellRefNode(ASTNode):
    ref: str  # raw text like "A1", "$B$2", "Sheet1!C3"
    node_type: NodeType = field(default=NodeType.CELL_REF, init=False)


@dataclass
class RangeRefNode(ASTNode):
    ref: str  # raw text like "A1:B10", "Sheet2!A1:C3"
    node_type: NodeType = field(default=NodeType.RANGE_REF, init=False)


@dataclass
class BinaryOpNode(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode
    node_type: NodeType = field(default=NodeType.BINARY_OP, init=False)


@dataclass
class UnaryOpNode(ASTNode):
    op: str  # "-" or "+"
    operand: ASTNode
    node_type: NodeType = field(default=NodeType.UNARY_OP, init=False)


@dataclass
class FunctionCallNode(ASTNode):
    name: str
    args: list[ASTNode]
    node_type: NodeType = field(default=NodeType.FUNCTION_CALL, init=False)


@dataclass
class ErrorNode(ASTNode):
    message: str
    node_type: NodeType = field(default=NodeType.ERROR, init=False)


# ── Tokenizer ──

class TokenType(Enum):
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    CELL_REF = auto()     # A1, $B$2, Sheet1!A1
    RANGE_REF = auto()    # A1:B10
    FUNCTION = auto()     # SUM(
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    OP_ADD = auto()       # +
    OP_SUB = auto()       # -
    OP_MUL = auto()       # *
    OP_DIV = auto()       # /
    OP_POW = auto()       # ^
    OP_PCT = auto()       # % (postfix: 10% → 0.1)
    OP_AMP = auto()       # & (string concat)
    OP_EQ = auto()        # =
    OP_NE = auto()        # <>
    OP_LT = auto()        # <
    OP_GT = auto()        # >
    OP_LE = auto()        # <=
    OP_GE = auto()        # >=
    ERROR = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    pos: int = 0


# Regex patterns for tokenizer
_NUM_RE = re.compile(r"\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")
_STR_RE = re.compile(r'"([^"]*)"')
_IDENT_RE = re.compile(r"[A-Za-z_][\w]*")
# Cell/range: optional Sheet!, then $?COL$?ROW, optional :$?COL$?ROW
_REF_RE = re.compile(
    r"(?:[A-Za-z_][\w]*!)?"
    r"\$?[A-Za-z]{1,3}\$?\d{1,7}"
    r"(?::\$?[A-Za-z]{1,3}\$?\d{1,7})?"
)
_ERROR_RE = re.compile(r"#[A-Z/!?]+[!?]?")


def tokenize(formula: str) -> list[Token]:
    """Tokenize a formula string into tokens."""
    tokens: list[Token] = []
    i = 0
    s = formula.strip()

    while i < len(s):
        ch = s[i]

        # Skip whitespace
        if ch in (" ", "\t"):
            i += 1
            continue

        # String literal
        if ch == '"':
            m = _STR_RE.match(s, i)
            if m:
                tokens.append(Token(TokenType.STRING, m.group(1), i))
                i = m.end()
                continue
            else:
                raise FormulaParseError(f"Unterminated string at position {i}")

        # Error values like #DIV/0!, #N/A, #VALUE!, #REF!, #NAME?, #NULL!, #NUM!, #CIRCULAR!
        if ch == "#":
            m = _ERROR_RE.match(s, i)
            if m:
                tokens.append(Token(TokenType.ERROR, m.group(0), i))
                i = m.end()
                continue

        # Number
        if ch.isdigit() or (ch == "." and i + 1 < len(s) and s[i + 1].isdigit()):
            m = _NUM_RE.match(s, i)
            if m:
                tokens.append(Token(TokenType.NUMBER, m.group(0), i))
                i = m.end()
                # Check for % postfix
                if i < len(s) and s[i] == "%":
                    tokens.append(Token(TokenType.OP_PCT, "%", i))
                    i += 1
                continue

        # Identifier: could be function name, boolean, or cell/range ref
        if ch.isalpha() or ch == "_" or ch == "$":
            # First try: identifier (letters/digits/underscore)
            ident_m = _IDENT_RE.match(s, i)
            if ident_m or ch == "$":
                ident = ident_m.group(0) if ident_m else ""
                ident_end = ident_m.end() if ident_m else i

                # Check for Sheet!Ref pattern
                if ident_end < len(s) and s[ident_end] == "!":
                    ref_m = _REF_RE.match(s, i)
                    if ref_m:
                        ref_text = ref_m.group(0)
                        if ":" in ref_text:
                            tokens.append(Token(TokenType.RANGE_REF, ref_text, i))
                        else:
                            tokens.append(Token(TokenType.CELL_REF, ref_text, i))
                        i = ref_m.end()
                        continue

                # Check for boolean
                if ident.upper() in ("TRUE", "FALSE"):
                    tokens.append(Token(TokenType.BOOLEAN, ident.upper(), i))
                    i = ident_end
                    continue

                # Check for function call (name followed by '(')
                if ident_end < len(s) and s[ident_end] == "(":
                    tokens.append(Token(TokenType.FUNCTION, ident.upper(), i))
                    i = ident_end  # don't skip '(' — consumed as LPAREN
                    continue

                # Check for cell ref or range ref (letters+digits pattern)
                ref_m = _REF_RE.match(s, i)
                if ref_m and (ch == "$" or re.match(r"^[A-Za-z]{1,3}\d+", ident)):
                    ref_text = ref_m.group(0)
                    if ":" in ref_text:
                        tokens.append(Token(TokenType.RANGE_REF, ref_text, i))
                    else:
                        tokens.append(Token(TokenType.CELL_REF, ref_text, i))
                    i = ref_m.end()
                    continue

                # If it matches just letters (no digits), it's an unknown identifier
                if ident and not re.match(r"^[A-Za-z]{1,3}\d+$", ident):
                    raise FormulaParseError(f"Unknown identifier '{ident}' at position {i}")

                # Fallback: try as cell ref
                if ident and re.match(r"^[A-Za-z]{1,3}\d+$", ident):
                    tokens.append(Token(TokenType.CELL_REF, ident, i))
                    i = ident_end
                    continue

                raise FormulaParseError(f"Unexpected character '{ch}' at position {i}")

        # Operators
        if ch == "(":
            tokens.append(Token(TokenType.LPAREN, "(", i)); i += 1; continue
        if ch == ")":
            tokens.append(Token(TokenType.RPAREN, ")", i)); i += 1; continue
        if ch == ",":
            tokens.append(Token(TokenType.COMMA, ",", i)); i += 1; continue
        if ch == "+":
            tokens.append(Token(TokenType.OP_ADD, "+", i)); i += 1; continue
        if ch == "-":
            tokens.append(Token(TokenType.OP_SUB, "-", i)); i += 1; continue
        if ch == "*":
            tokens.append(Token(TokenType.OP_MUL, "*", i)); i += 1; continue
        if ch == "/":
            tokens.append(Token(TokenType.OP_DIV, "/", i)); i += 1; continue
        if ch == "^":
            tokens.append(Token(TokenType.OP_POW, "^", i)); i += 1; continue
        if ch == "&":
            tokens.append(Token(TokenType.OP_AMP, "&", i)); i += 1; continue
        if ch == "=":
            tokens.append(Token(TokenType.OP_EQ, "=", i)); i += 1; continue
        if ch == "<":
            if i + 1 < len(s) and s[i + 1] == ">":
                tokens.append(Token(TokenType.OP_NE, "<>", i)); i += 2; continue
            if i + 1 < len(s) and s[i + 1] == "=":
                tokens.append(Token(TokenType.OP_LE, "<=", i)); i += 2; continue
            tokens.append(Token(TokenType.OP_LT, "<", i)); i += 1; continue
        if ch == ">":
            if i + 1 < len(s) and s[i + 1] == "=":
                tokens.append(Token(TokenType.OP_GE, ">=", i)); i += 2; continue
            tokens.append(Token(TokenType.OP_GT, ">", i)); i += 1; continue
        if ch == "%":
            tokens.append(Token(TokenType.OP_PCT, "%", i)); i += 1; continue

        raise FormulaParseError(f"Unexpected character '{ch}' at position {i}")

    tokens.append(Token(TokenType.EOF, "", len(s)))
    return tokens


# ── Parser (Recursive Descent) ──

class FormulaParseError(Exception):
    pass


class Parser:
    """
    Recursive descent parser for spreadsheet formulas.

    Precedence (low to high):
    1. Comparison: =, <>, <, >, <=, >=
    2. Concatenation: &
    3. Addition: +, -
    4. Multiplication: *, /
    5. Exponentiation: ^
    6. Unary: -, +
    7. Postfix: %
    8. Primary: number, string, bool, cell ref, range, function call, (expr)
    """

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def expect(self, tt: TokenType) -> Token:
        t = self.peek()
        if t.type != tt:
            raise FormulaParseError(f"Expected {tt.name}, got {t.type.name} ('{t.value}') at pos {t.pos}")
        return self.advance()

    def parse(self) -> ASTNode:
        if self.peek().type == TokenType.EOF:
            raise FormulaParseError("Empty formula")
        node = self.parse_comparison()
        if self.peek().type != TokenType.EOF:
            t = self.peek()
            raise FormulaParseError(f"Unexpected token '{t.value}' at pos {t.pos}")
        return node

    def parse_comparison(self) -> ASTNode:
        left = self.parse_concat()
        while self.peek().type in (TokenType.OP_EQ, TokenType.OP_NE, TokenType.OP_LT, TokenType.OP_GT, TokenType.OP_LE, TokenType.OP_GE):
            op = self.advance()
            right = self.parse_concat()
            left = BinaryOpNode(op=op.value, left=left, right=right)
        return left

    def parse_concat(self) -> ASTNode:
        left = self.parse_addition()
        while self.peek().type == TokenType.OP_AMP:
            self.advance()
            right = self.parse_addition()
            left = BinaryOpNode(op="&", left=left, right=right)
        return left

    def parse_addition(self) -> ASTNode:
        left = self.parse_multiplication()
        while self.peek().type in (TokenType.OP_ADD, TokenType.OP_SUB):
            op = self.advance()
            right = self.parse_multiplication()
            left = BinaryOpNode(op=op.value, left=left, right=right)
        return left

    def parse_multiplication(self) -> ASTNode:
        left = self.parse_exponent()
        while self.peek().type in (TokenType.OP_MUL, TokenType.OP_DIV):
            op = self.advance()
            right = self.parse_exponent()
            left = BinaryOpNode(op=op.value, left=left, right=right)
        return left

    def parse_exponent(self) -> ASTNode:
        left = self.parse_unary()
        if self.peek().type == TokenType.OP_POW:
            self.advance()
            right = self.parse_exponent()  # right-associative
            left = BinaryOpNode(op="^", left=left, right=right)
        return left

    def parse_unary(self) -> ASTNode:
        if self.peek().type == TokenType.OP_SUB:
            self.advance()
            operand = self.parse_unary()
            return UnaryOpNode(op="-", operand=operand)
        if self.peek().type == TokenType.OP_ADD:
            self.advance()
            return self.parse_unary()
        return self.parse_postfix()

    def parse_postfix(self) -> ASTNode:
        node = self.parse_primary()
        if self.peek().type == TokenType.OP_PCT:
            self.advance()
            # x% → x / 100
            node = BinaryOpNode(op="/", left=node, right=NumberNode(value=100.0))
        return node

    def parse_primary(self) -> ASTNode:
        t = self.peek()

        if t.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(value=float(t.value))

        if t.type == TokenType.STRING:
            self.advance()
            return StringNode(value=t.value)

        if t.type == TokenType.BOOLEAN:
            self.advance()
            return BooleanNode(value=t.value == "TRUE")

        if t.type == TokenType.ERROR:
            self.advance()
            return ErrorNode(message=t.value)

        if t.type == TokenType.CELL_REF:
            self.advance()
            return CellRefNode(ref=t.value)

        if t.type == TokenType.RANGE_REF:
            self.advance()
            return RangeRefNode(ref=t.value)

        if t.type == TokenType.FUNCTION:
            name = self.advance().value
            self.expect(TokenType.LPAREN)
            args: list[ASTNode] = []
            if self.peek().type != TokenType.RPAREN:
                args.append(self.parse_comparison())
                while self.peek().type == TokenType.COMMA:
                    self.advance()
                    args.append(self.parse_comparison())
            self.expect(TokenType.RPAREN)
            return FunctionCallNode(name=name, args=args)

        if t.type == TokenType.LPAREN:
            self.advance()
            node = self.parse_comparison()
            self.expect(TokenType.RPAREN)
            return node

        raise FormulaParseError(f"Unexpected token '{t.value}' ({t.type.name}) at pos {t.pos}")


def parse_formula(formula: str) -> ASTNode:
    """Parse a formula string into an AST. Strips leading '=' if present."""
    text = formula.strip()
    if text.startswith("="):
        text = text[1:]
    if not text:
        raise FormulaParseError("Empty formula")
    tokens = tokenize(text)
    parser = Parser(tokens)
    return parser.parse()
