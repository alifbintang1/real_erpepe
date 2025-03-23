import unittest
from src.resolvent_generator import generate_resolvents_minimal

class TestResolventGenerator(unittest.TestCase):
    def test_resolvent_generation(self):
        # Simple CNF: (p ∨ q) and (¬p ∨ r)
        S = {frozenset({1, 2}), frozenset({-1, 3})}
        R = generate_resolvents_minimal(S)
        # The resolvent on p should be: (q ∨ r)
        expected = frozenset({2, 3})
        self.assertIn(expected, R)

if __name__ == '__main__':
    unittest.main()
