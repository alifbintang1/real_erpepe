import unittest
from src.cnf_parser import parse_cnf
import os

class TestCNFParser(unittest.TestCase):
    def test_parse_simple(self):
        # Create a temporary CNF content.
        cnf_content = """
c This is a comment
p cnf 3 2
1 -3 0
2 3 -1 0
"""
        test_file = "tests/temp.cnf"
        with open(test_file, "w") as f:
            f.write(cnf_content)
        
        num_vars, clauses = parse_cnf(test_file)
        self.assertEqual(num_vars, 3)
        self.assertEqual(len(clauses), 2)
        self.assertIn(frozenset({1, -3}), clauses)
        self.assertIn(frozenset({2, 3, -1}), clauses)
        os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
