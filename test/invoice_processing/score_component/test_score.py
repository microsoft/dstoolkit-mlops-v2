"""
Unit tests for the evaluation step in the experimentation framework
"""

import unittest
import yaml
import pandas as pd
from src.invoice_processing.score_component.score.score import (
    evaluate,
    get_gt_and_pred_data_for_evaluation,
)


class TestScore(unittest.TestCase):
    """
    Test evaluate output for perfect match
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

    def test_evaluate_perfect_match(self):

        ground_truth = [
            {
                "reference_id": "12345",
                "lineItems": [
                    {
                        "serviceStartDate": "12/29/23",
                        "serviceEndDate": "12/30/23",
                        "amount": 324,
                        "description": "Child care",
                    },
                    {
                        "serviceStartDate": "1/1/24",
                        "serviceEndDate": "3/1/24",
                        "amount": 134,
                        "description": "After school program",
                    },
                    {
                        "serviceStartDate": "4/1/24",
                        "serviceEndDate": "4/1/24",
                        "amount": 76,
                        "description": "Learning center",
                    },
                ],
            }
        ]

        pred = {
            "12345.jpg": {
                "invoice": {
                    "lineItems": [
                        {
                            "serviceStartDate": "12/29/23",
                            "serviceEndDate": "12/30/23",
                            "amount": 324,
                            "text": "Child care",
                            "miles": None,
                        },
                        {
                            "serviceStartDate": "1/1/24",
                            "serviceEndDate": "3/1/24",
                            "amount": 134,
                            "text": "After school program",
                            "miles": None,
                        },
                        {
                            "serviceStartDate": "4/1/24",
                            "serviceEndDate": "4/1/24",
                            "amount": 76,
                            "text": "Learning center",
                            "miles": None,
                        },
                    ],
                }
            }
        }

        (
            final_results_df,
            overall_accuracy,
            gt_invoices_number,
            pred_invoices_number,
            all_unmatched_gt,
            all_unmatched_pred,
            comparison_df_all,
            best_matches_all,
            all_matches_results_total,
            overall_precision,
            overall_recall,
        ) = evaluate(pred, ground_truth, self.score_config)
        self.assertEqual(overall_accuracy, 1.0)
        self.assertEqual(overall_precision, 1.0)
        self.assertEqual(overall_recall, 1.0)

    def test_evaluate_partial_match(self):
        """
        Test evaluate output for partial match
        """
        ground_truth = [
            {
                "reference_id": "12345",
                "lineItems": [
                    {
                        "serviceStartDate": "12/26/23",
                        "serviceEndDate": "12/30/23",
                        "amount": 324,
                        "description": "Child care",
                    },
                    {
                        "serviceStartDate": "1/1/24",
                        "serviceEndDate": "3/1/24",
                        "amount": 134,
                        "description": "Tuition",
                    },
                    {
                        "serviceStartDate": "4/1/24",
                        "serviceEndDate": "4/1/24",
                        "amount": 76,
                        "description": "Learning center",
                    },
                ],
            }
        ]

        pred = {
            "12345.jpg": {
                "invoice": {
                    "lineItems": [
                        {
                            "serviceStartDate": "12/29/23",
                            "serviceEndDate": "12/30/23",
                            "amount": 324,
                            "text": "Child care",
                            "miles": None,
                        },
                        {
                            "serviceStartDate": "1/1/24",
                            "serviceEndDate": "3/1/24",
                            "amount": 134,
                            "text": "After school program",
                            "miles": None,
                        },
                        {
                            "serviceStartDate": "4/1/24",
                            "serviceEndDate": "4/1/24",
                            "amount": 76,
                            "text": "Learning center",
                            "miles": None,
                        },
                        {
                            "serviceStartDate": "12/30/23",
                            "serviceEndDate": "12/31/23",
                            "amount": 267,
                            "text": "Emergency room",
                            "miles": None,
                        },
                    ],
                }
            }
        }

        (
            final_results_df,
            overall_accuracy,
            gt_invoices_number,
            pred_invoices_number,
            all_unmatched_gt,
            all_unmatched_pred,
            comparison_df_all,
            best_matches_all,
            all_matches_results_total,
            overall_precision,
            overall_recall,
        ) = evaluate(pred, ground_truth, self.score_config)
        self.assertEqual(round(overall_accuracy, 3), 0.634)

    def test_evaluate_no_match(self):
        """
        Test evaluate output for no match
        """
        ground_truth = [
            {
                "reference_id": "12345",
                "lineItems": [
                    {
                        "serviceStartDate": "12/26/23",
                        "serviceEndDate": "12/30/23",
                        "amount": 324,
                        "description": "Child care",
                    },
                    {
                        "serviceStartDate": "1/1/24",
                        "serviceEndDate": "3/1/24",
                        "amount": 134,
                        "description": "Tuition",
                    },
                    {
                        "serviceStartDate": "4/1/24",
                        "serviceEndDate": "4/1/24",
                        "amount": 76,
                        "description": "Learning center",
                    },
                ],
            }
        ]

        pred = {
            "12345.jpg": {
                "invoice": {
                    "lineItems": [
                        {
                            "serviceStartDate": "",
                            "serviceEndDate": "12/31/23",
                            "amount": 267,
                            "text": "Emergency room",
                            "miles": None,
                        },
                        {
                            "serviceStartDate": "2/1/24",
                            "serviceEndDate": "",
                            "amount": 152,
                            "text": "After school program",
                            "miles": None,
                        },
                        {
                            "serviceStartDate": "",
                            "serviceEndDate": "5/1/24",
                            "amount": 74,
                            "text": "Medicines",
                            "miles": None,
                        },
                    ]
                }
            }
        }

        (
            final_results_df,
            overall_accuracy,
            gt_invoices_number,
            pred_invoices_number,
            all_unmatched_gt,
            all_unmatched_pred,
            comparison_df_all,
            best_matches_all,
            all_matches_results_total,
            overall_precision,
            overall_recall,
        ) = evaluate(pred, ground_truth, self.score_config)
        self.assertEqual(round(overall_accuracy, 3), 0.07)
        self.assertEqual(overall_precision, 1.0)
        self.assertEqual(overall_recall, 1.0)

    def test_evaluate_partial_match_for_recall(self):
        """
        Test evaluate output for partial match, for recall.
        """
        ground_truth = [
            {
                "reference_id": "12345",
                "lineItems": [
                    {
                        "serviceStartDate": "12/26/23",
                        "serviceEndDate": "12/30/23",
                        "amount": 324,
                        "description": "Child care",
                    },
                    {
                        "serviceStartDate": "1/1/24",
                        "serviceEndDate": "3/1/24",
                        "amount": 134,
                        "description": "Tuition",
                    },
                    {
                        "serviceStartDate": "4/1/24",
                        "serviceEndDate": "4/1/24",
                        "amount": 76,
                        "description": "Learning center",
                    },
                    {
                        "serviceStartDate": "4/5/24",
                        "serviceEndDate": "4/7/24",
                        "amount": 94,
                        "description": "Lunch fee",
                    },
                ],
            }
        ]

        pred = {
            "12345.jpg": {
                "InvoiceDetails": {
                    "lineItems": [
                        {
                            "serviceStartDate": "12/29/23",
                            "serviceEndDate": "12/30/23",
                            "amount": 324,
                            "description": "Child care",
                            "miles": None,
                        },
                        {
                            "serviceStartDate": "1/1/24",
                            "serviceEndDate": "3/1/24",
                            "amount": 134,
                            "description": "After school program",
                            "miles": None,
                        },
                        {
                            "serviceStartDate": "4/1/24",
                            "serviceEndDate": "4/1/24",
                            "amount": 76,
                            "description": "Learning center",
                            "miles": None,
                        },
                    ],
                }
            }
        }

        (
            final_results_df,
            overall_accuracy,
            gt_invoices_number,
            pred_invoices_number,
            all_unmatched_gt,
            all_unmatched_pred,
            comparison_df_all,
            best_matches_all,
            all_matches_results_total,
            overall_precision,
            overall_recall,
        ) = evaluate(pred, ground_truth, self.score_config)
        self.assertEqual(round(overall_recall, 3), 0.75)

    def test_evaluate_partial_match_for_precision(self):
        """
        Test evaluate output for partial match, for precision.
        """
        ground_truth = [
            {
                "reference_id": "12345",
                "lineItems": [
                    {
                        "serviceStartDate": "12/26/23",
                        "serviceEndDate": "12/30/23",
                        "amount": 324,
                        "description": "Child care",
                    },
                    {
                        "serviceStartDate": "1/1/24",
                        "serviceEndDate": "3/1/24",
                        "amount": 134,
                        "description": "Tuition",
                    },
                    {
                        "serviceStartDate": "4/1/24",
                        "serviceEndDate": "4/1/24",
                        "amount": 76,
                        "description": "Learning center",
                    },
                ],
            }
        ]

        pred = {
            "12345.jpg": {
                "InvoiceDetails": {
                    "lineItems": [
                        {
                            "serviceStartDate": "12/29/23",
                            "serviceEndDate": "12/30/23",
                            "amount": 324,
                            "description": "Child care",
                            "miles": None,
                        },
                        {
                            "serviceStartDate": "1/1/24",
                            "serviceEndDate": "3/1/24",
                            "amount": 134,
                            "description": "After school program",
                            "miles": None,
                        },
                        {
                            "serviceStartDate": "4/1/24",
                            "serviceEndDate": "4/1/24",
                            "amount": 76,
                            "description": "Learning center",
                            "miles": None,
                        },
                        {
                            "serviceStartDate": "9/3/24",
                            "serviceEndDate": "9/3/24",
                            "amount": 100,
                            "description": "Registration fee",
                            "miles": None,
                        },
                    ],
                }
            }
        }

        (
            final_results_df,
            overall_accuracy,
            gt_invoices_number,
            pred_invoices_number,
            all_unmatched_gt,
            all_unmatched_pred,
            comparison_df_all,
            best_matches_all,
            all_matches_results_total,
            overall_precision,
            overall_recall,
        ) = evaluate(pred, ground_truth, self.score_config)
        self.assertEqual(round(overall_precision, 3), 0.75)

    def test_get_gt_and_pred_data_for_evaluation(self):
        ground_truth = {
            "reference_id": "12345.jpg",
            "lineItems": [
                {
                    "description": "Dependent care",
                    "amount": 120,
                    "serviceStartDate": "07/07/2021",
                    "serviceEndDate": "07/23/2021",
                },
                {
                    "description": "Lunch fee",
                    "amount": 64,
                    "serviceStartDate": "07/07/2021",
                    "serviceEndDate": "07/23/2021",
                },
            ],
        }

        predictions = {
            "invoice": {
                "lineItems": [],
            }
        }
        gt_data, pred_data = get_gt_and_pred_data_for_evaluation(
            ground_truth, predictions
        )
        self.assertTrue("miles" not in pred_data.columns.tolist())


if __name__ == "__main__":
    unittest.main()
