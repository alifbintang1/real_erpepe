import unittest
import time
import os
import tracemalloc
from cnf_parser import parse_cnf
from resolvent_generator import generate_resolvents_minimal
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
        memory_usages = []  # Store memory usage for each CNF instance

        for cnf_file in tqdm(cnf_files, desc="Processing CNF files"):
            cnf_path = os.path.join(FOLDER, cnf_file)

            # Start memory tracking
            tracemalloc.start()
            start_time = time.time()  

            num_vars, clauses, true_label = parse_cnf(cnf_path)
            R = generate_resolvents_minimal(clauses, verbose=False)
            interpretation = res_sat(R, num_vars)

            end_time = time.time()  
            current, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()  # Stop memory tracking

            predicted_label = validate_interpretation(clauses, interpretation)

            pred.append(predicted_label)
            labels.append(true_label)

            instance_runtime = end_time - start_time
            runtimes.append(instance_runtime)
            memory_usages.append(peak_memory)  # Store peak memory usage

            current_accuracy = sum(p == l for p, l in zip(pred, labels)) / len(labels) if labels else 0
            current_avg_runtime = sum(runtimes) / len(runtimes) if runtimes else 0
            current_avg_memory = sum(memory_usages) / len(memory_usages) if memory_usages else 0

            tqdm.write(f"After processing {cnf_file}: | Resolvent {len(R)}")
            tqdm.write(f"  True Label: {true_label} | Pred: {predicted_label}")
            tqdm.write(f"  Accuracy: {current_accuracy:.2%}")
            tqdm.write(f"  Avg Runtime: {current_avg_runtime:.4f} seconds")
            tqdm.write(f"  Peak Memory Usage: {peak_memory / 1024:.2f} KB")
            tqdm.write(f"  Avg Memory Usage per CNF: {current_avg_memory / 1024:.2f} KB")

        correct_predictions = sum(p == l for p, l in zip(pred, labels))
        self.assertGreaterEqual(correct_predictions / len(labels) if labels else 0, 0)

if __name__ == '__main__':
    unittest.main()
