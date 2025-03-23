from tqdm import tqdm
from utils import complement


def filter_minimal(clauses):
    """
    Given a set of clauses, return a new set containing only the minimal clauses.
    A clause c is minimal if there is no other clause d (c != d) with d ⊆ c.
    """
    minimal = set(clauses)  # Start with a copy of all clauses
    for c in clauses:
        for d in clauses:
            if c != d and d.issubset(c):
                # c is not minimal because d is a subset of c
                if c in minimal:
                    minimal.remove(c)
                break
    return minimal

def generate_resolvents_minimal(clauses, max_iterations=2, max_resolvents=10000, verbose = True):
    """
    Generate the resolution closure R = RES(S) with only minimal resolvents.
    
    Parameters:
        clauses: an iterable of frozenset (the original clauses)
        max_iterations: limit on the number of resolution iterations
        max_resolvents: limit on the total number of clauses (to avoid explosion)
        
    Returns:
        R: set of minimal resolvents (each clause is a frozenset of ints)
    """
    R = set(clauses)
    iteration = 0
    new_resolvents = set()
    changed = True
    cutoff = 0

    while changed and iteration < max_iterations and len(R) < max_resolvents:
        if verbose: 
            print(f"Starting iteration {iteration}...")
        iteration += 1
        changed = False
        current_clauses = list(R)
        # Try resolving every pair of clauses
        for i in range(len(current_clauses)):
            for j in range(i+1, len(current_clauses)):
                c1 = current_clauses[i]
                c2 = current_clauses[j]
                for literal in c1:
                    if -literal in c2:
                        resolvent = (c1 - {literal}) | (c2 - {-literal})
                        # Skip tautologies (clauses containing both literal and its complement)
                        if any(l in resolvent and -l in resolvent for l in resolvent):
                            continue
                        resolvent = frozenset(resolvent)
                        if resolvent not in R and resolvent not in new_resolvents:
                            new_resolvents.add(resolvent)
                            # cutoff += 1
            #     if cutoff >= max_resolvents:
            #         print(f"Reached the limit of {max_resolvents} resolvents, stopping.")
            #         break
            # if cutoff >= max_resolvents:
            #     break 
                
        if new_resolvents:
            R |= new_resolvents
            # Filter R to keep only minimal resolvents
            R = filter_minimal(R)
            if verbose:
                print(f"Iteration {iteration}: added {len(new_resolvents)} new resolvents; minimal total now: {len(R)}")
            new_resolvents = set()
            changed = True
        else:
            if verbose:
                print(f"Iteration {iteration}: no new resolvents found, stopping.")
    return R

