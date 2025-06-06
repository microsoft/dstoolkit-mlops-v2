"""Class that performs exact matches for amounts"""

import logging

from .base_matcher import BaseMatcher
from ..utils import preprocess_amount

log = logging.getLogger(__name__)


class AmountExactMatcher(BaseMatcher):
    """
    Calculate amount exact match.
    """

    def amount_exact_match(self, amount1, amount2):
        """
        Find out whether the amounts in ground truth and prediction are equal
        Args:
            amount_str1: First amount value
            amount_str2: Second amount value
        Returns:
            match: whether the compared values are equal (exact match)
        """
        match = False
        parsed_amount1 = preprocess_amount(amount1)
        parsed_amount2 = preprocess_amount(amount2)
        diff = abs(float(parsed_amount1) - float(parsed_amount2))
        if diff == 0:
            match = True
        else:
            match = False
        return match

    def get_matcher_name(self):
        """
        return matcher name.
        """
        return "amount_exact_match"

    def get_match(self, comparison_df, field_name):
        """
        Get match result per line item.
        """
        match_df = comparison_df.apply(
            lambda x: self.amount_exact_match(
                x[f"{field_name}_gt"], x[f"{field_name}_pred"]
            ),
            axis=1,
        )
        return match_df
