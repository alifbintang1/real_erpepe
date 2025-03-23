#!/usr/bin/env python3
import sys
import re


#############################################
# 1. Tokenization and Parsing
#############################################


def tokenize(s):
    """
    Splits the input string into tokens.
    Recognized tokens: variables, '->', '<->', '&', '|', '~', '(' and ')'.
    """
    tokens = []
    token_specification = [
        ("SKIP", r"\s+"),
        ("IMPLIES", r"->"),
        ("IFF", r"<->"),
        ("AND", r"&"),
        ("OR", r"\|"),
        ("NOT", r"~"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("VAR", r"[A-Za-z][A-Za-z0-9_]*"),
    ]
    tok_regex = "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in token_specification)
    for mo in re.finditer(tok_regex, s):
        kind = mo.lastgroup
        value = mo.group()
        if kind == "SKIP":
            continue
        tokens.append((kind, value))
    return tokens


class Parser:
    """
    Recursive descent parser for propositional formulas.
    Grammar:
        formula       := implication
        implication   := equivalence (IMPLIES equivalence)*
        equivalence   := disjunction (IFF disjunction)*
        disjunction   := conjunction (OR conjunction)*
        conjunction   := unary (AND unary)*
        unary         := NOT unary | atom
        atom          := VAR | LPAREN formula RPAREN
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, token_type=None):
        token = self.peek()
        if token is None:
            return None
        if token_type and token[0] != token_type:
            raise SyntaxError(f"Expected token {token_type} but got {token}")
        self.pos += 1
        return token

    def parse_formula(self):
        return self.parse_implication()

    def parse_implication(self):
        left = self.parse_equivalence()
        token = self.peek()
        while token and token[0] == "IMPLIES":
            self.consume("IMPLIES")
            right = self.parse_equivalence()
            left = ("implies", left, right)
            token = self.peek()
        return left

    def parse_equivalence(self):
        left = self.parse_disjunction()
        token = self.peek()
        while token and token[0] == "IFF":
            self.consume("IFF")
            right = self.parse_disjunction()
            left = ("iff", left, right)
            token = self.peek()
        return left

    def parse_disjunction(self):
        left = self.parse_conjunction()
        token = self.peek()
        while token and token[0] == "OR":
            self.consume("OR")
            right = self.parse_conjunction()
            left = ("or", left, right)
            token = self.peek()
        return left

    def parse_conjunction(self):
        left = self.parse_unary()
        token = self.peek()
        while token and token[0] == "AND":
            self.consume("AND")
            right = self.parse_unary()
            left = ("and", left, right)
            token = self.peek()
        return left

    def parse_unary(self):
        token = self.peek()
        if token and token[0] == "NOT":
            self.consume("NOT")
            operand = self.parse_unary()
            return ("not", operand)
        else:
            return self.parse_atom()

    def parse_atom(self):
        token = self.peek()
        if token is None:
            raise SyntaxError("Unexpected end of input")
        if token[0] == "VAR":
            self.consume("VAR")
            return ("var", token[1])
        elif token[0] == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_formula()
            self.consume("RPAREN")
            return expr
        else:
            raise SyntaxError(f"Unexpected token: {token}")


#############################################
# 2. Eliminate Implications/Biconditionals
#############################################


def eliminate_implications(ast):
    """
    Recursively replaces implications and biconditionals.
      - A -> B becomes ~A or B.
      - A <-> B becomes (A -> B) & (B -> A).
    """
    if isinstance(ast, tuple):
        typ = ast[0]
        if typ == "implies":
            return (
                "or",
                ("not", eliminate_implications(ast[1])),
                eliminate_implications(ast[2]),
            )
        elif typ == "iff":
            a = eliminate_implications(ast[1])
            b = eliminate_implications(ast[2])
            return ("and", ("or", ("not", a), b), ("or", ("not", b), a))
        else:
            return (ast[0], *[eliminate_implications(sub) for sub in ast[1:]])
    else:
        return ast


#############################################
# 3. Tseitin Transformation to CNF
#############################################


class TseitinTransformer:
    def __init__(self):
        self.var_counter = 1
        self.mapping = {}  # mapping from original variable names to integers
        self.clauses = []

    def get_fresh_var(self):
        v = self.var_counter
        self.var_counter += 1
        return v

    def transform(self, ast):
        """
        Returns an integer representing the subformula.
        For non-atomic nodes a new variable is introduced with clauses
        enforcing the equivalence between the variable and the subformula.
        """
        if isinstance(ast, tuple):
            typ = ast[0]
            if typ == "var":
                name = ast[1]
                if name not in self.mapping:
                    self.mapping[name] = self.get_fresh_var()
                return self.mapping[name]
            elif typ == "not":
                v = self.get_fresh_var()
                a = self.transform(ast[1])
                # v <-> ¬a is equivalent to: (v ∨ a) and (¬v ∨ ¬a)
                self.clauses.append([v, a])
                self.clauses.append([-v, -a])
                return v
            elif typ == "and":
                v = self.get_fresh_var()
                a = self.transform(ast[1])
                b = self.transform(ast[2])
                # v <-> (a and b) is equivalent to:
                # (¬v ∨ a), (¬v ∨ b), (v ∨ ¬a ∨ ¬b)
                self.clauses.append([-v, a])
                self.clauses.append([-v, b])
                self.clauses.append([v, -a, -b])
                return v
            elif typ == "or":
                v = self.get_fresh_var()
                a = self.transform(ast[1])
                b = self.transform(ast[2])
                # v <-> (a or b) is equivalent to:
                # (v ∨ ¬a), (v ∨ ¬b), (¬v ∨ a ∨ b)
                self.clauses.append([v, -a])
                self.clauses.append([v, -b])
                self.clauses.append([-v, a, b])
                return v
            else:
                raise ValueError(f"Unknown operator: {typ}")
        else:
            raise ValueError("Invalid AST node")

    def tseitin(self, ast):
        # First, eliminate implications to work only with ~, & and |
        ast = eliminate_implications(ast)
        root = self.transform(ast)
        # Finally, assert that the whole formula is true
        self.clauses.append([root])
        return self.clauses, self.var_counter - 1


def write_dimacs(clauses, num_vars, filename):
    """
    Writes the CNF in DIMACS format to a file.
    """
    with open(filename, "w") as f:
        f.write(f"p cnf {num_vars} {len(clauses)}\n")
        for clause in clauses:
            clause_str = " ".join(map(str, clause)) + " 0\n"
            f.write(clause_str)


#############################################
# 4. Main Routine
#############################################


def main():
    if len(sys.argv) < 3:
        print("Usage: python prop_to_cnf.py input_formula.txt output.cnf")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Read the input formula (ignoring comment lines that start with #)
    with open(input_file, "r") as f:
        formula_lines = [line for line in f if not line.strip().startswith("#")]
    formula_str = " ".join(formula_lines).strip()

    tokens = tokenize(formula_str)
    parser = Parser(tokens)
    ast = parser.parse_formula()

    transformer = TseitinTransformer()
    clauses, num_vars = transformer.tseitin(ast)

    write_dimacs(clauses, num_vars, output_file)
    print(f"CNF written to {output_file}")


if __name__ == "__main__":
    main()
