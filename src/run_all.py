import os
import sys
from cnf_parser import parse_cnf
from resolvent_generator import generate_resolvents_minimal
from res_sat import res_sat
from validator import validate_interpretation

def process_cnf_file(cnf_file):
    """Process a single CNF file with the resolution-based SAT solver."""
    print(f"\n{'='*80}\nProcessing CNF file: {cnf_file}\n{'='*80}")
    
    try:
        num_vars, clauses = parse_cnf(cnf_file)
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
        
        return True
    except Exception as e:
        print(f"Error processing file {cnf_file}: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_all.py <directory-path>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        sys.exit(1)
    
    print(f"Processing all CNF files in directory: {directory}")
    
    cnf_files = [f for f in os.listdir(directory) if f.endswith('.cnf')]
    
    if not cnf_files:
        print("No CNF files found in the specified directory.")
        sys.exit(1)
    
    print(f"Found {len(cnf_files)} CNF files to process.")
    
    results = {}
    for i, cnf_file in enumerate(cnf_files, 1):
        full_path = os.path.join(directory, cnf_file)
        print(f"\nProcessing file {i}/{len(cnf_files)}: {cnf_file}")
        success = process_cnf_file(full_path)
        results[cnf_file] = success
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY OF RESULTS")
    print("="*80)
    print(f"Total files processed: {len(cnf_files)}")
    successful = sum(1 for success in results.values() if success)
    print(f"Successfully processed: {successful}")
    print(f"Failed: {len(cnf_files) - successful}")
    
    if len(cnf_files) - successful > 0:
        print("\nFailed files:")
        for cnf_file, success in results.items():
            if not success:
                print(f"- {cnf_file}")

if __name__ == "__main__":
    main()