"""Class that performs exact matches for dates"""

import logging
from typing import Dict
import pandas as pd
import Levenshtein
from ..utils import normalize_string
from .base_matcher import BaseMatcher

log = logging.getLogger(__name__)


class LevenshteinMatcher(BaseMatcher):

    def get_matcher_name(self):
        return "levenshtein"

    def calculate_levenshtein_ratio(self, string1: str, string2: str):
        """
        Calculates the Levenshtein ratio between two strings.

        The Levenshtein ratio is a measure of the similarity between two strings,
        defined as the ratio of the Levenshtein distance to the length of the longer string.
        It range from 0 to 1, where 1 indicates identical strings and 0 indicates
        completely different strings.

        Args:
        string1 (str): The first string
        string2 (str): The second string

        Returns:
        levenshtein_ratio (float): The calculated Lenshtein ratio.
        """
        normalized_gt = normalize_string(str(string1))
        normalized_gen = normalize_string(str(string2))
        levenshtein_ratio = Levenshtein.ratio(normalized_gt, normalized_gen)
        rounded_levenshtein_ratio = round(levenshtein_ratio, 3)
        return rounded_levenshtein_ratio

    def get_match(self, comparison_df, field_name):
        """
        Get match result per line item. Calculates Levenshtein ratio.
        """
        match_df = comparison_df.apply(
            lambda x: self.calculate_levenshtein_ratio(
                x[f"{field_name}_gt"], x[f"{field_name}_pred"]
            ),
            axis=1,
        )
        return match_df

    def find_best_matches(self, comparison_df: pd.DataFrame, fuzzy_match_config: Dict):
        """
        For every line item in the ground truth data, find the most similar
        line item in the predictions
        Args:
            comparison_df: a dataframe which is the cartesian product of the
            line items inthe ground truth and the predictions datasets
        Returns:
            A dictionary of the best matches: {"fuzzy_match_method_name": best_matches_df}
        """

        levenshtein_ratio_thr = fuzzy_match_config["field_match_threshold"]
        remaining_comparisons = comparison_df.copy()
        best_matches_list_levenshtein = []
        best_matches_dict = {}
        for i in range(comparison_df["gt_index"].nunique()):
            max_exact_matches = remaining_comparisons["exact_match_sum"].max()
            similarity_thr = max_exact_matches + levenshtein_ratio_thr
            curr_max_similarity = remaining_comparisons["similarity_score"].max()
            if curr_max_similarity >= similarity_thr:
                max_similarity_index = remaining_comparisons[
                    "similarity_score"
                ].argmax()
                best_match = remaining_comparisons.iloc[max_similarity_index]
                best_match_gt = best_match["gt_index"]
                best_match_pred = best_match["pred_index"]
                best_matches_list_levenshtein.append(
                    {"gt_index": best_match_gt, "pred_index": best_match_pred}
                )
                index_to_drop = remaining_comparisons[
                    (remaining_comparisons["gt_index"] == best_match_gt)
                    | (remaining_comparisons["pred_index"] == best_match_pred)
                ].index
                remaining_comparisons.drop(index_to_drop, inplace=True)
            else:
                continue
        best_matches_dict["levenshtein"] = best_matches_list_levenshtein
        return best_matches_dict
