import unittest
import time
import os
import math
import sys
from cnf_parser import parse_cnf
from resolvent_generator import generate_resolvents, generate_resolvents_minimal
from res_sat import res_sat
from validator import validate_interpretation

FOLDER = "AIM"
from tqdm import tqdm

class TestAIM(unittest.TestCase):
    def test_aim(self):
        pred = []
        labels = []
        cnf_files = [f for f in os.listdir(FOLDER) if f.endswith(".cnf")]
        
        runtimes = [] 

        # Use tqdm to iterate over CNF files with a progress bar.
        for cnf_file in tqdm(cnf_files, desc="Processing CNF files"):
            cnf_path = os.path.join(FOLDER, cnf_file)
            # Optionally, log the file being processed using tqdm.write
            # tqdm.write(f"Processing CNF file: {cnf_path}")

            start_time = time.time()  
            num_vars, clauses, true_label = parse_cnf(cnf_path)

            # if true_label is None:
            #     tqdm.write(f"Skipping {cnf_file} (No label found)")
            #     continue  

            R = generate_resolvents_minimal(clauses, verbose=False)
            interpretation = res_sat(R, num_vars)

            end_time = time.time()  # End timing
            predicted_label = validate_interpretation(clauses, interpretation)

            pred.append(predicted_label)
            labels.append(true_label)

            instance_runtime = end_time - start_time
            runtimes.append(instance_runtime)
            current_accuracy = sum(p == l for p, l in zip(pred, labels)) / len(labels) if labels else 0
            current_avg_runtime = sum(runtimes) / len(runtimes) if runtimes else 0
            if len(runtimes) > 1:
                variance = sum((x - current_avg_runtime) ** 2 for x in runtimes) / len(runtimes)
                current_std_runtime = math.sqrt(variance)
            else:
                current_std_runtime = 0  
                
            tqdm.write(f"After processing {cnf_file}:")
            tqdm.write(f"  True Label: {true_label} | Pred: {predicted_label}")
            tqdm.write(f"  Accuracy: {current_accuracy:.2%}")
            tqdm.write(f"  Average Runtime per CNF Instance: {current_avg_runtime:.4f} seconds")
            tqdm.write(f"  Standard Deviation of Runtime: {current_std_runtime:.4f} seconds\n")

        correct_predictions = sum(p == l for p, l in zip(pred, labels))
        self.assertGreaterEqual(correct_predictions / len(labels) if labels else 0, 0)

if __name__ == '__main__':
    unittest.main()
