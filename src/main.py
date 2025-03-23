import sys
from cnf_parser import parse_cnf
from resolvent_generator import generate_resolvents_minimal
from res_sat import res_sat
from validator import validate_interpretation


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path-to-cnf-file>")
        sys.exit(1)
    
    cnf_file = sys.argv[1]
    print(f"Reading CNF file: {cnf_file}")
    num_vars, clauses, _ = parse_cnf(cnf_file)
    print(f"Number of variables: {num_vars}")
    print(f"Number of clauses: {len(clauses)}")
    
    print("Generating resolution closure (this may take some time for large inputs)...")
    R = generate_resolvents_minimal(clauses)
    print(f"Resolution closure generated with {len(R)} clauses.")
    
    print("Running RES-SAT procedure...")
    interpretation = res_sat(R, num_vars)
    print("Satisfying interpretation (as a set of literals):")
    print(interpretation)

    # Validate the interpretation against the original CNF clauses
    if validate_interpretation(clauses, interpretation):
        print("Validation passed: the interpretation satisfies the CNF formula.")
    else:
        print("Validation failed: the interpretation does NOT satisfy the CNF formula.")
    
if __name__ == "__main__":
    main()
