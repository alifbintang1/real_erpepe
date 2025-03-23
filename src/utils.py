def complement(literal: int) -> int:
    """
    Returns the complement of a literal.
    If literal is positive, returns its negative and vice versa.
    """
    return -literal

def complement_clause(clause: set) -> set:
    """
    Returns the set of complementary literals for a given clause.
    """
    return {complement(l) for l in clause}
