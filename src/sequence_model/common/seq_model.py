"""This module defines the custom model object."""
from collections import defaultdict
from nltk.util import ngrams
from typing import Tuple
import pickle


class NgramModel:
    """
    A class used to represent an N-gram Model for text prediction.

    Attributes
    ----------
    max_prior_token_length : int
        The maximum length of prior tokens to consider for n-gram prediction.
    max_ngram_length : int
        The maximum length of n-grams to compute from the corpus.
    counts : defaultdict
        A dictionary to store the counts of each n-gram.
    token_count : int
        The total number of tokens in the corpus.
    max_top_n : int
        The maximum number of top predictions to consider.
    vocab_size : int
        The size of the vocabulary in the corpus.
    uniform_prob : float
        The uniform probability for unigrams.
    probs : dict
        A dictionary to store the conditional probabilities of n-grams.
    lookup_tables : dict
        A dictionary to store the lookup tables for top n predictions.

    Methods
    -------
    count(corpus)
        Counts all n-grams in the given corpus.
    calculate_unigram_prob(unigram)
        Calculates the conditional probability for a unigram.
    calculate_multigram_prob(ngram)
        Calculates the conditional probability for a higher n-gram (multigram).
    train()
        Calculates the conditional probabilities for all n-grams in the training text.
    lookup_dict_top_n(ngram_length, top_n)
        Constructs the probability lookup table for a given n-gram length.
    predict(prior_tokens, top_n, verbose=False)
        Predicts the top_n next tokens given the prior tokens.
    save(save_path)
        Saves the model to a specified path.
    load(model_dict)
        Loads the model from a specified path.
    """

    def __init__(self, max_prior_token_length: int = None, max_top_n: int = 10) -> None:
        """
        Initialize the NgramModel with specified parameters.

        Parameters
        ----------
        max_prior_token_length : int, optional
            The maximum length of prior tokens to consider for n-gram prediction. Default is None.
        max_top_n : int, optional
            The maximum number of top predictions to consider. Default is 10.

        Attributes
        ----------
        max_prior_token_length : int
            The maximum length of prior tokens to consider for n-gram prediction.
        max_ngram_length : int
            The maximum length of n-grams to compute from the corpus.
        counts : defaultdict
            A dictionary to store the counts of each n-gram.
        token_count : int
            The total number of tokens in the corpus.
        max_top_n : int
            The maximum number of top predictions to consider.
        vocab_size : int
            The size of the vocabulary in the corpus.
        uniform_prob : float
            The uniform probability for unigrams.
        probs : dict
            A dictionary to store the conditional probabilities of n-grams.
        lookup_tables : dict
            A dictionary to store the lookup tables for top n predictions.
        """
        self.max_prior_token_length = max_prior_token_length
        self.max_ngram_length = (
            self.max_prior_token_length + 1
        )  # Compute ngrams of this length from corpus
        self.counts = defaultdict(int)
        self.token_count = None
        self.max_top_n = max_top_n
        self.vocab_size = None
        self.uniform_prob = None
        self.probs = {}
        self.lookup_tables = {}

    def count(self, corpus):
        """
        Count the occurrences of n-grams in the given corpus.

        This method updates the token count, n-gram counts, vocabulary size, and uniform probability
        based on the provided corpus. It iterates through n-grams of varying lengths (from 1 to max_ngram_length)
        and updates the counts for each n-gram.

        Parameters:
        corpus (list): A list of tokens representing the corpus.

        Updates:
        self.token_count (int): The total number of tokens in the corpus.
        self.counts (dict): A dictionary where keys are n-grams and values are their counts.
        self.vocab_size (int): The number of unique tokens (unigrams) in the corpus.
        self.uniform_prob (float): The uniform probability of any token in the vocabulary.
        """
        self.token_count = len(corpus)

        for ngram_length in range(1, self.max_ngram_length + 1):
            ngram_list = list(ngrams(corpus, ngram_length))
            for ngram in ngram_list:
                self.counts[ngram] += 1

        self.vocab_size = len(
            list(ngram for ngram in self.counts.keys() if len(ngram) == 1)
        )
        self.uniform_prob = 1 / (self.vocab_size)

    def calculate_unigram_prob(self, unigram: Tuple[str]) -> None:
        """
        Calculate the probability of a given unigram.

        This method computes the probability of a unigram by dividing its count by the total number of tokens
        in the corpus. The result is stored in the `self.probs` dictionary.

        Parameters:
        unigram (Tuple[str]): A tuple representing the unigram for which the probability is to be calculated.

        Updates:
        self.probs (dict): A dictionary where keys are unigrams and values are their probabilities.
        """
        prob_nom = self.counts[unigram]
        prob_denom = self.token_count
        self.probs[unigram] = prob_nom / prob_denom

    def calculate_multigram_prob(self, ngram: Tuple[str]) -> None:
        """
        Calculate the probability of an n-gram based on its preceding n-1 gram.

        This method computes the probability of a given n-gram by dividing its count
        by the count of its preceding n-1 gram. The result is stored in the `probs` dictionary.

        Parameters:
        ngram (Tuple[str]): The n-gram for which the probability is to be calculated.

        Updates:
        self.probs (dict): A dictionary where keys are n-grams and values are their calculated probabilities.
        """
        prevgram = ngram[:-1]
        prob_nom = self.counts[ngram]
        prob_denom = self.counts[prevgram]
        self.probs[ngram] = prob_nom / prob_denom

    def train(self) -> None:
        """
        Train the n-gram model by calculating probabilities and constructing lookup tables.

        This method iterates through all n-grams in the counts dictionary and calculates their probabilities.
        For unigrams, it calls the `calculate_unigram_prob` method, and for higher-order n-grams, it calls the
        `calculate_multigram_prob` method. Additionally, it constructs lookup tables for the top N next tokens
        for each n-gram length up to `max_ngram_length`.

        Updates:
        self.probs (dict): A dictionary where keys are n-grams and values are their calculated probabilities.
        self.lookup_tables (dict): A dictionary where keys are n-gram lengths and values are lookup dictionaries
                                of the top N next tokens.
        """
        for ngram in self.counts:
            if len(ngram) == 1:
                self.calculate_unigram_prob(ngram)
            else:
                self.calculate_multigram_prob(ngram)
        # For each ngram_length, construct the lookup dict of the top_n next
        # tokens where top_n is max_top_n
        for ngram_length in range(1, self.max_ngram_length + 1):
            self.lookup_tables[ngram_length] = self.lookup_dict_top_n(
                ngram_length, self.max_top_n
            )

    def lookup_dict_top_n(self, ngram_length, top_n):
        """
        Construct a lookup dictionary of the top N next tokens for a given n-gram length.

        This method extracts the probabilities of n-grams of the specified length, sorts them in descending order,
        and constructs a nested dictionary where the keys are the n-grams (excluding the last token) and the values
        are the top N next tokens based on their probabilities.

        Parameters:
        ngram_length (int): The length of the n-grams to consider.
        top_n (int): The number of top next tokens to include for each n-gram.

        Returns:
        dict: A nested dictionary where keys are n-grams (excluding the last token) and values are lists of the
        top N next tokens.
        """
        # get probs for ngram_length of interest, sort
        subset_probs = {
            k: self.probs[k] for k in list(self.probs.keys()) if len(k) == ngram_length
        }
        sorted_probs = dict(
            sorted(subset_probs.items(), reverse=True, key=lambda item: item[1])
        )

        # convert tuple to nested dict
        d = defaultdict(defaultdict(dict).copy)  # lambda: defaultdict(dict))
        for k, v in sorted_probs.items():
            d[k[0:-1]][k[-1]] = v

        # only keep key/value combo associated with n highest probs
        filtered_d = defaultdict(
            defaultdict(dict).copy
        )
        for k, v in d.items():
            filtered_d[k] = list(v.keys())[0:top_n]

        return filtered_d

    def predict(self, prior_tokens, top_n):
        """
        Predict the top N next tokens based on the given prior tokens.

        This method predicts the most likely next tokens given a sequence of prior tokens. It uses the n-gram model
        to find the top N predictions. If the length of prior tokens is less than the maximum n-gram length, it either
        returns the top N unigrams if no prior tokens are provided, or it looks up the top N predictions from the
        lookup tables. If no predictions are found, it recursively trims the prior tokens and tries again. If the
        length of prior tokens exceeds the maximum n-gram length, it prints a warning message.

        Parameters:
        prior_tokens (list): A list of tokens representing the prior context.
        top_n (int): The number of top predictions to return.

        Returns:
        list: A list of the top N predicted next tokens.
        """
        prior_ngram_length = len(prior_tokens)

        if prior_ngram_length < self.max_ngram_length:
            if prior_ngram_length == 0:
                subset_probs = {
                    key: value for key, value in self.probs.items() if len(key) == 1
                }
                tokens = list(
                    dict(
                        sorted(
                            subset_probs.items(), reverse=True, key=lambda item: item[1]
                        )
                    ).keys()
                )[0:top_n]
                tokens_topn = list(
                    map(lambda x: x[0], tokens[0: min(top_n, len(tokens))])
                )
                return tokens_topn
            else:
                if self.lookup_tables[prior_ngram_length + 1].get(prior_tokens):
                    topn_preds = self.lookup_tables[prior_ngram_length + 1][
                        prior_tokens
                    ]
                    return topn_preds[0:top_n]
                else:
                    # Recursively trim tokens
                    prior_tokens = prior_tokens[1:]
                    if len(prior_tokens) > 0:
                        return self.predict(prior_tokens, top_n)
                    else:
                        return []
        else:
            print(
                "Context too long. Should be less than max ngram length used to build and train model."
            )
            return []

    def save(self, save_path: str):
        """Serialize the model dictionary for reuseability."""
        # Build dict object to serialize
        model_dict = {
            "max_prior_token_length": self.max_prior_token_length,
            "max_ngram_length": self.max_ngram_length,
            "probs": self.probs,
            "lookup_tables": self.lookup_tables,
            "vocab_size": self.vocab_size,
            "max_top_n": self.max_top_n,
        }
        with open(save_path, "wb") as f:
            pickle.dump(model_dict, f)

    def load(self, model_dict: str):
        """De-serialize the model dictionary to use a pretrained model from disc."""
        with open(model_dict, "rb") as f:
            model_dict = pickle.load(f)

        self.max_prior_token_length = model_dict["max_prior_token_length"]
        self.max_ngram_length = model_dict["max_ngram_length"]
        self.probs = model_dict["probs"]
        self.lookup_tables = model_dict["lookup_tables"]
        self.vocab_size = model_dict["vocab_size"]
        self.max_top_n = model_dict["max_top_n"]
