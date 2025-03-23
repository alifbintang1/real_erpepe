from utils import complement, complement_clause

def res_sat(R, num_vars: int):
    """
    Implements the RES-SAT procedure.
    
    Input:
      - R: set of resolvent clauses (each clause is a frozenset of ints)
      - num_vars: number of atoms (assumed to be numbered 1 to num_vars)
    
    Returns:
      - T: a set of literals representing a satisfying interpretation.
    """
    T = set()
    for i in range(1, num_vars+1):
        candidate = T | {i}  # Assume variable i is True
        found_clause = False
        for clause in R:
            # ¬clause is the set of complements of the literals in clause.
            if complement_clause(clause).issubset(candidate):
                found_clause = True
                break
        if found_clause:
            T.add(-i)
        else:
            T.add(i)
    return T
