"""
This module contains the ExtractionEvaluator class, which provides evaluation methods for data extraction from images.
The class includes functionalities for calculating various metrics and generating reports.

Classes: ExtractionEvaluation: a class for evaluation of data extraction from images
"""

from typing import Dict, List
import pandas as pd
import logging
from .matchers.date_exact_matcher import DateExactMatcher
from .matchers.amount_exact_matcher import AmountExactMatcher
from .matchers.levenshtein_matcher import LevenshteinMatcher
from .matchers.text_exact_matcher import TextExactMatcher

log = logging.getLogger(__name__)


class ExtractionEvaluator:
    """
    A comprehensive evaluator for comparing invoice details between
    ground truth and predictions.

    This class currently supports single file evaluation
    with flexible comparison strategies.
    """

    def __init__(
        self,
        fuzzy_match_config: Dict,
        exact_match_fields: List[str],
        matchers_dict: Dict,
        find_best_matches_strategy: str,
    ):
        """
        Initialize the base matcher with ground truth data.

        Args:
            fuzzy_match_config: fuzzy match configuration
            exact_match_fields: fields that are compared by exact match
            matchers_dict: field to matcher type mapping
            find_best_matches_strategy: The startegy to use when trying
            to find the most similar line items
        """
        # Configuration for line item matching
        self.fuzzy_match_config = fuzzy_match_config

        # exact match fields list
        self.exact_match_fields = exact_match_fields

        # fields to matcher type
        self.matchers_dict = matchers_dict

        # find best matches strategy
        self.find_best_matches_strategy = find_best_matches_strategy

    def get_matcher(self, matcher_class_name: str):
        """
        Create an instance of the requested matcher.
        Args: matcher_class_name: Name of the matcher per
            field as defined in the experiment config file.
        Returns:
            Instance of the requested matcher class
        """
        if matcher_class_name == "date_exact_match":
            return DateExactMatcher()
        elif matcher_class_name == "amount_exact_match":
            return AmountExactMatcher()
        elif matcher_class_name == "description_levenshtein":
            return LevenshteinMatcher()
        elif matcher_class_name == "text_exact_match":
            return TextExactMatcher()
        else:
            print("matcher undefined!")
            return None

    def get_matcher_for_best_matches_strategy(self, best_matches_strategy: str):
        """
        Get find best matches strategy.
        """
        if best_matches_strategy == "levenshtein":
            return LevenshteinMatcher()
        elif best_matches_strategy == "text_exact_match":
            return TextExactMatcher()
        else:
            print("best matches strategy is not defined!")
            return None

    def get_match_method(self, matcher_name: str):
        """
        Get match method from matcher name.
            Args: matcher_name: name of the matcher
            Returns: match method (currently exact_match or levenshtein)
        """
        match_method = ""
        matcher_name_split = matcher_name.split("_")
        if len(matcher_name_split) > 1:
            match_method = f"{matcher_name_split[1]}_{matcher_name_split[2]}"
        else:
            match_method = matcher_name
        return match_method

    def compare_line_item_values_per_invoice(
        self,
        ground_truth_df: pd.DataFrame,
        predictions_df: pd.DataFrame,
    ):
        """
        Compare the line items in the ground trith data with the line items in the prediction data.
        Find exact matches if exist and calculate fuzzy match metrics for relevent fields.
        Args:
            ground_truth_df: A dataframe in which each column is a different
            extracted field (startDate, endDate, amount, description)
            and each row represents a different line item in the invoice
            predictions_df: Same as ground_truth_df only for model data extraction
        Returns:
            Dataframe with exact and fuzzy match metrics for all line items (all vs. all)
        """
        field_names = []
        ground_truth_df["gt_index"] = range(ground_truth_df.shape[0])
        predictions_df["pred_index"] = range(predictions_df.shape[0])
        comparison_df = pd.merge(
            ground_truth_df, predictions_df, how="cross", suffixes=["_gt", "_pred"]
        )
        for field_name in self.matchers_dict:
            curr_matcher = self.get_matcher(self.matchers_dict.get(field_name))
            matcher_name = curr_matcher.get_matcher_name()
            match_method = self.get_match_method(matcher_name)
            comparison_df[f"{field_name}_{match_method}"] = curr_matcher.get_match(
                comparison_df, field_name
            )
            field_names.append(f"{field_name}_{match_method}")

        exact_match_fields = [x for x in field_names if "exact" in x]
        comparison_df["exact_match_sum"] = comparison_df[exact_match_fields].sum(axis=1)
        comparison_df["similarity_score"] = comparison_df[field_names].sum(axis=1)
        return comparison_df

    def get_match_results(
        self,
        comparison_df: pd.DataFrame(),
    ):
        """
        Report the line items match results and additional datasets for error analysis.
        Args:
            comparison_df (pd.DataFrame): dataframe will all possible combinations
            of line items from the ground truth and the predictions.
            best_matches_dict (Dict): Dictionary with lists per fuzzy match method,
            of pairs of matched ground truth and prediction line items.
        Returns:
        """
        unmatched_gt = pd.DataFrame()
        gt_cols = []
        unmatched_pred = pd.DataFrame()
        pred_cols = []
        match_results_df = pd.DataFrame()
        best_matches_matcher = self.get_matcher_for_best_matches_strategy(
            self.find_best_matches_strategy
        )
        description_matcher_name = best_matches_matcher.get_matcher_name()
        best_matches_dict = best_matches_matcher.find_best_matches(
            comparison_df, self.fuzzy_match_config
        )
        best_matches_pairs_list = best_matches_dict[description_matcher_name]

        best_matches_pairs_df = pd.DataFrame(best_matches_pairs_list)
        best_matches_df = pd.merge(
            best_matches_pairs_df,
            comparison_df,
            on=["gt_index", "pred_index"],
            how="left",
        )
        best_matches_gt_index = best_matches_pairs_df["gt_index"].unique().tolist()
        best_matches_pred_index = best_matches_pairs_df["pred_index"].unique().tolist()
        unmatched_gt = comparison_df[
            ~comparison_df["gt_index"].isin(best_matches_gt_index)
        ].drop_duplicates(subset=["gt_index"])
        unmatched_pred = comparison_df[
            ~comparison_df["pred_index"].isin(best_matches_pred_index)
        ].drop_duplicates(subset=["pred_index"])
        gt_cols = [x for x in comparison_df.columns.tolist() if "_gt" in x]
        pred_cols = [x for x in comparison_df.columns.tolist() if "_pred" in x]
        match_results_df = pd.concat(
            [best_matches_df, unmatched_gt[gt_cols], unmatched_pred[pred_cols]]
        ).fillna(0)
        return (
            match_results_df,
            unmatched_gt[gt_cols],
            unmatched_pred[pred_cols],
            best_matches_df,
        )

    def calculate_evaluation_metrics_per_field_in_invoice(
        self, match_results_df: pd.DataFrame
    ):
        """
        Calculate the evaluation metric per invoice per field. Currently supports accuracy.
        Args:
            match_results_df (pd.DataFrame): A dataframe with all line items from
            the ground truth and the predictions: line items of the ground truth and
            their match from the predictions, line items from the ground truth and the
            predictions that were not matched.
        Returns:
            results_df (DataFrame): A dataframe with the accuracy results
            per line item for a single invoice.
        """
        field_col_names = [
            f"{x}_{self.get_match_method(self.get_matcher(self.matchers_dict.get(x)).get_matcher_name())}"
            for x in self.matchers_dict.keys()
        ]
        matches_eval_fields = match_results_df[field_col_names]
        results_df = self.calculate_mean_accuracy_per_invoice(matches_eval_fields)
        results_df = results_df.reset_index().rename(columns={"index": "field_name"})
        results_df = results_df[["field_name", "accuracy"]].sort_values(by="field_name")
        return results_df

    def calculate_mean_accuracy_per_invoice(self, matches_eval_fields: pd.DataFrame):
        """
        Calcualte the mean accuracy per field in a single invoice.
        Args:
            matches_eval_fields (pd.DataFrame): A dataframe with the ressulting matches
            per line item in the ground truth data which includes only the fields we would
            like to include in the evaluation.
        Returns:
            mean_accuracy_df (pd.DataFrame): A dataframe with the
            accuracy results.
        """
        mean_accuracy_df = matches_eval_fields.mean()
        accuracy_df = pd.DataFrame(mean_accuracy_df.T).rename(columns={0: "accuracy"})
        accuracy_df = accuracy_df.round({"accuracy": 3})
        return accuracy_df

    def calculate_mean_accuracy_per_batch(self, all_invoices_results: pd.DataFrame):
        """
        Calcualte the mean accuracy per field in a batch of invoices.
        Args:
            all_invoices_results (pd.DataFrame): A dataframe with the mean accuracy
            results of all invoices in the experiment.
        Returns:
            final_results_df (pd.DataFrame): A dataframe with the mean
            accuracy results across all invoices.
            overall_accuracy (float): Mean accuracy across all fields and invoices.
        """
        final_results_df = (
            all_invoices_results[["field_name", "accuracy"]]
            .groupby(by="field_name")
            .mean()
            .reset_index()
        )
        overall_accuracy = round(final_results_df["accuracy"].mean(), 3)
        final_results_df = final_results_df[["field_name", "accuracy"]]
        final_results_df = final_results_df.round({"accuracy": 3})
        return overall_accuracy, final_results_df

    def calculate_precision_per_record(
        self, unmatched_pred: pd.DataFrame(), best_matches_df: pd.DataFrame()
    ):
        """
        This function calculates the precision per invoice (record).
        Args:
            unmatched_pred: Dataframe of line items in the extracted data that
            were not matched to any ground truth line item (defined as FPs).
            best_matches_df: Dataframe with the matched line items from
            the ground truth data and the extractions.
        Returns:
            precision (float): The precision metric
        """
        tp = 0
        fp = 0
        fp = unmatched_pred.shape[0]
        tp = best_matches_df.shape[0]
        precision = tp / (tp + fp)
        return precision

    def calculate_recall_per_record(
        self, unmatched_gt: pd.DataFrame(), best_matches_df: pd.DataFrame()
    ):
        """
        This function calculates the precision per invoice (record).
        Args:
            unmatched_gt: Dataframe of line items in the ground truth data that
            were not matched to any extracted line item (defined as FNs).
            best_matches_df: Dataframe with the matched line items from
            the ground truth data and the extractions.
        Returns:
            recall (float): The recall metric
        """
        tp = 0
        fn = 0
        fn = unmatched_gt.shape[0]
        tp = best_matches_df.shape[0]
        recall = tp / (tp + fn)
        return recall
