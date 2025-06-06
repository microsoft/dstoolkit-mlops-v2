"""
Unit tests for utils.py of the evaluation step of the experimentation framework.
"""

import unittest
import pandas as pd
from src.invoice_processing.score_component.score.utils import normalize_string


class TestScore(unittest.TestCase):

    def test_normalize_str(self):
        """
        Test normalize_str.
        """
        value = "   (   vaLue  )  "
        normalized_str = normalize_string(value)
        self.assertEqual(normalized_str, "(value)")


if __name__ == "__main__":
    unittest.main()
