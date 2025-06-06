"""Class that performs exact matches for dates"""

import logging

from .base_matcher import BaseMatcher
from ..utils import preprocess_date

log = logging.getLogger(__name__)


class DateExactMatcher(BaseMatcher):

    def dates_exact_match(self, date_str1: str, date_str2: str):
        """
        Find out whether the dates are identical.
        Args:
            date_str1: First date value
            date_str2: Second date value
        Returns:
            match: whether the compared values are equal (exact match)
        """
        match = False
        try:
            date1 = preprocess_date(date_str1)
            date2 = preprocess_date(date_str2)
            if date1 == date2:
                match = True
            else:
                match = False
        except ValueError:
            log.debug(
                """One or more of the date strings could not be parsed into date type,
                performing string comparison instead"""
            )
            if date_str1 == date_str2:
                match = True
            else:
                match = False
        return match

    def get_matcher_name(self):
        """
        return matcher name.
        """
        return "date_exact_match"

    def get_match(self, comparison_df, field_name):
        """
        Get match result per line item.
        """
        match_df = comparison_df.apply(
            lambda x: self.dates_exact_match(
                x[f"{field_name}_gt"], x[f"{field_name}_pred"]
            ),
            axis=1,
        )
        return match_df
