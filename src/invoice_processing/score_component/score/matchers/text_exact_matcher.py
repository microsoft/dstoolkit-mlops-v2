"""Class that performs exact matches for text"""

import logging

from .base_matcher import BaseMatcher
from ..utils import normalize_string

log = logging.getLogger(__name__)


class TextExactMatcher(BaseMatcher):

    def get_matcher_name(self):
        """
        return matcher name.
        """
        return "text_exact_match"

    def get_match(self, comparison_df, field_name):
        """
        Get match result per line item.
        """
        match_df = comparison_df.apply(
            lambda x: self.text_exact_match(
                x[f"{field_name}_gt"], x[f"{field_name}_pred"]
            ),
            axis=1,
        )
        return match_df

    def text_exact_match(self, str1: str, str2: str):
        """
        Find out whether the dates are identical.
        Args:
            str1: First string value
            date_str2: Second string value
        Returns:
            match: whether the compared values are equal (exact match)
        """
        normalized_str1 = normalize_string(str(str1))
        normalized_str2 = normalize_string(str(str2))
        match = False
        if normalized_str1 == normalized_str2:
            match = True
        else:
            match = False
        return match

    def find_best_matches(self, comparison_df):
        """
        For every line item in the ground truth data, find the most similar
        line item in the predictions
        Args:
            comparison_df: a dataframe which is the cartesian product of the
            line items inthe ground truth and the predictions datasets
        Returns:
            A dictionary of the best matches: {"match_method_name": best_matches_df}
        """
        remaining_comparisons = comparison_df.copy()
        best_matches_list = []
        best_matches_dict = {}
        for i in range(comparison_df["gt_index"].nunique()):
            curr_max_similarity = remaining_comparisons["similarity_score"].max()
            if curr_max_similarity > 0:
                max_similarity_index = remaining_comparisons[
                    "similarity_score"
                ].argmax()
                best_match = remaining_comparisons.iloc[max_similarity_index]
                best_match_gt = best_match["gt_index"]
                best_match_pred = best_match["pred_index"]
                best_matches_list.append(
                    {"gt_index": best_match_gt, "pred_index": best_match_pred}
                )
                index_to_drop = remaining_comparisons[
                    (remaining_comparisons["gt_index"] == best_match_gt)
                    | (remaining_comparisons["pred_index"] == best_match_pred)
                ].index
                remaining_comparisons.drop(index_to_drop, inplace=True)
            else:
                continue
        best_matches_dict["exact_match"] = best_matches_list
        return best_matches_dict
