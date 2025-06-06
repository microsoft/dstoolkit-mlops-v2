"""
Unit tests for functions of the ExtractionEvaluator class in the experimentation framework
"""

import unittest
import yaml
import pandas as pd
from src.invoice_processing.score_component.score.score import (
    create_extraction_evaluator,
    get_score_config,
)
from src.invoice_processing.score_component.score.matchers.levenshtein_matcher import (
    LevenshteinMatcher,
)
from src.invoice_processing.score_component.score.matchers.text_exact_matcher import (
    TextExactMatcher,
)


class TestExtractionEvaluator(unittest.TestCase):
    """
    Test extraction_evaluator.py
    """

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.score_config = str(
            yaml.safe_load(
                open(
                    "test/invoice_processing/score_component/test_experiment_config.yaml"
                )
            )["score_config"]
        )

    def setup_datasets(self):
        """
        Setup ground truth data and a corresponding predictions data,
        whose fields are a perfect match.
        Returns:
            ground_truth_df: ground truth dataframe
            pred_df: predictions dataframe
        """

        ground_truth_df = pd.DataFrame(
            {
                "gt_index": [0, 1, 2, 3],
                "serviceStartDate": ["1/3/24", "12/29/23", "1/4/24", "1/10/24"],
                "serviceEndDate": ["1/9/24", "12/30/23", "1/4/24", "1/12/24"],
                "amount": [134, 324, 78, 200],
                "description": [
                    "Child care service",
                    "After school program",
                    "Learning center",
                    "Swimming lessons",
                ],
            }
        )
        pred_df = pd.DataFrame(
            {
                "pred_index": [0, 1, 2, 3],
                "serviceStartDate": ["12/29/23", "1/1/24", "1/4/24", ""],
                "serviceEndDate": ["12/30/23", "1/9/24", "1/4/24", "3/1/24"],
                "amount": [324, 134, 76, 100],
                "description": [
                    "After school program",
                    "Child care",
                    "Learning center",
                    "Summer camp",
                ],
                "miles": [None, None, None, None],
            }
        )
        return ground_truth_df, pred_df

    def test_find_best_matches_levenshtein(self):
        """
        Test find_best_matches function that is meant to find the best
        matches from the predictions data to the ground truth data.
        """
        score_config_dict = get_score_config(self.score_config)
        fuzzy_match_config = score_config_dict["fuzzy_match_config"]
        ground_truth_df, pred_df = self.setup_datasets()
        evaluator = create_extraction_evaluator(self.score_config)
        comparison_df = evaluator.compare_line_item_values_per_invoice(
            ground_truth_df, pred_df
        )
        best_matches_dict = LevenshteinMatcher().find_best_matches(
            comparison_df, fuzzy_match_config
        )
        best_matches_df = pd.DataFrame(best_matches_dict["levenshtein"])
        matches_indices = list(
            zip(best_matches_df["gt_index"], best_matches_df["pred_index"])
        )
        self.assertTrue((0.0, 1.0) in matches_indices)
        self.assertTrue((1.0, 0.0) in matches_indices)
        self.assertTrue((2.0, 2.0) in matches_indices)

    def test_find_best_matches_base_exact_matcher(self):
        """
        Test find_best_matches function that is meant to find the best
        matches from the predictions data to the ground truth data.
        """
        ground_truth_df, pred_df = self.setup_datasets()
        evaluator = create_extraction_evaluator(self.score_config)
        comparison_df = evaluator.compare_line_item_values_per_invoice(
            ground_truth_df, pred_df
        )
        best_matches_dict = TextExactMatcher().find_best_matches(comparison_df)
        best_matches_df = pd.DataFrame(best_matches_dict["exact_match"])
        matches_indices = list(
            zip(best_matches_df["gt_index"], best_matches_df["pred_index"])
        )
        self.assertTrue((0.0, 1.0) in matches_indices)
        self.assertTrue((1.0, 0.0) in matches_indices)
        self.assertTrue((2.0, 2.0) in matches_indices)


if __name__ == "__main__":
    unittest.main()
