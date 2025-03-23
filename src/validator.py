def validate_interpretation(clauses, interpretation):
    """
    Check whether the given interpretation satisfies the CNF formula.

    Args:
        clauses (iterable of frozenset): Each clause is a frozenset of integers (literals).
        interpretation (set of int): A set of literals representing the assignment. 
                                     For each variable p, exactly one of p or -p should be in this set.

    Returns:
        bool: True if every clause is satisfied (i.e., has at least one literal in the interpretation), 
              False otherwise.
    """
    for clause in clauses:
        # A clause is satisfied if it has a non-empty intersection with the interpretation.
        if clause.isdisjoint(interpretation):
            return False
    return True
