import re

def parse_cnf(file_path: str):
    """
    Parses a CNF file in DIMACS format.
    
    Returns:
        num_vars (int): number of variables.
        clauses (list of frozenset): each clause is represented as a frozenset of integers.
    """
    clauses = []
    num_vars = None

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line == "" or line.startswith("c"):
                continue
            if line.startswith("p"):
                # Format: p cnf num_vars num_clauses
                tokens = line.split()
                if len(tokens) >= 4 and tokens[1] == "cnf":
                    num_vars = int(tokens[2])
                continue
            # Each clause line ends with a 0. Split the line into tokens.
            tokens = re.split(r'\s+', line)
            # Filter out any empty tokens and convert to int.
            literals = [int(tok) for tok in tokens if tok and int(tok) != 0]
            if literals:
                clauses.append(frozenset(literals))
    return num_vars, clauses
