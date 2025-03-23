import unittest
from src.cnf_parser import parse_cnf
from src.resolvent_generator import generate_resolvents
from src.res_sat import res_sat
import os

class TestResSat(unittest.TestCase):
    def test_res_sat_on_small_instance(self):
        # Create a small satisfiable CNF instance.
        cnf_content = """
c Example CNF
p cnf 2 2
1 0
2 0
"""
        test_file = "tests/temp.cnf"
        with open(test_file, "w") as f:
            f.write(cnf_content)
        
        num_vars, clauses = parse_cnf(test_file)
        R = generate_resolvents(clauses)
        interpretation = res_sat(R, num_vars)
        # For this CNF, both variables can be set to True.
        self.assertTrue(1 in interpretation or -1 in interpretation)
        self.assertTrue(2 in interpretation or -2 in interpretation)
        os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
