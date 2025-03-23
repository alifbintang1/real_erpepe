import os
import sys
import re
from cnf_parser import parse_cnf
from resolvent_generator import generate_resolvents_minimal
from res_sat import res_sat
from validator import validate_interpretation

def natural_sort_key(s):
    """
    Sort strings that contain numbers in a way that humans would expect.
    For example: aim-50-1_6-no-1.cnf comes before aim-100-1_6-no-1.cnf
    """
    # Extract the main number after "aim-"
    main_number_match = re.search(r'aim-(\d+)-', s)
    main_number = int(main_number_match.group(1)) if main_number_match else 0
    
    # Extract the secondary parameters in x_y format
    secondary_match = re.search(r'-(\d+)_(\d+)-', s)
    x = int(secondary_match.group(1)) if secondary_match else 0
    y = int(secondary_match.group(2)) if secondary_match else 0
    
    # Extract if it's yes/no
    yes_no = 1 if "yes" in s else 0
    
    # Extract the final number
    final_match = re.search(r'-(yes|no)-(\d+)\.cnf', s)
    final_number = int(final_match.group(2)) if final_match else 0
    
    # Return a tuple for sorting
    return (main_number, x, y, yes_no, final_number)

def process_cnf_file(cnf_file):
    """Process a single CNF file with the resolution-based SAT solver."""
    print(f"\n{'='*80}\nProcessing CNF file: {cnf_file}\n{'='*80}")
    
    try:
        num_vars, clauses, satisfiable = parse_cnf(cnf_file)
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
    
    # Get all CNF files
    cnf_files = [f for f in os.listdir(directory) if f.endswith('.cnf')]
    
    if not cnf_files:
        print("No CNF files found in the specified directory.")
        sys.exit(1)
    
    # Sort files using the natural sort key
    try:
        sorted_files = sorted(cnf_files, key=natural_sort_key)
    except Exception as e:
        print(f"Error during sorting: {str(e)}")
        print("Falling back to basic sort")
        sorted_files = sorted(cnf_files)
    
    print(f"Found {len(sorted_files)} CNF files to process.")
    print("Files will be processed in the following order:")
    for i, file in enumerate(sorted_files, 1):
        print(f"{i}. {file}")
    
    # Ask for confirmation
    response = 'y'
    if response.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    results = {}
    for i, cnf_file in enumerate(sorted_files, 1):
        full_path = os.path.join(directory, cnf_file)
        print(f"\nProcessing file {i}/{len(sorted_files)}: {cnf_file}")
        success = process_cnf_file(full_path)
        results[cnf_file] = success
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY OF RESULTS")
    print("="*80)
    print(f"Total files processed: {len(sorted_files)}")
    successful = sum(1 for success in results.values() if success)
    print(f"Successfully processed: {successful}")
    print(f"Failed: {len(sorted_files) - successful}")
    
    if len(sorted_files) - successful > 0:
        print("\nFailed files:")
        for cnf_file, success in results.items():
            if not success:
                print(f"- {cnf_file}")

if __name__ == "__main__":
    main()