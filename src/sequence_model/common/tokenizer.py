"""Learns a tokenizer from a training corpus. Tokenizes data accordingly."""

import json
from io import open
from pathlib import Path


class Tokenizer(object):
    """Creates tokenizer object with training and tokenization methods."""

    def __init__(self):
        """Initialize the tokenizer object."""
        self.eos_word = "[EOS]"
        self.unk_word = "[UNK]"
        self.words_to_i = {}
        self.i_to_words = {}
        self.vocab_size = None

    def load(self, path: str) -> "Tokenizer":
        """
        Load the tokenizer information to know how to tokenize the dataset.

        Args:
            path (str): The path to the saved tokenizer information file.

        Returns:
            Tokenizer: An initialized tokenizer instance.
        """
        with open(path, "rb") as f:
            t = json.load(f)

        tokenizer = Tokenizer()
        tokenizer.vocab_size = t["vocab_size"]
        tokenizer.words_to_i = t["words_to_i"]
        tokenizer.i_to_words = t["i_to_words"]

        return tokenizer

    def save(self, save_path):
        """Save out the tokenizer information to help us encode/decode later."""
        t = {
            "vocab_size": self.vocab_size,
            "eos_word": self.eos_word,
            "unk_word": self.unk_word,
            "words_to_i": self.words_to_i,
            "i_to_words": self.i_to_words,
        }
        jsonfile = Path(save_path)

        with open(jsonfile, "w", encoding="utf-8") as f:
            json.dump(t, f, ensure_ascii=False, indent=4)

    def train(self, corpus, save_path: str = ""):
        """
        Ingests the full corpus and trains a tokenizer on the corpus.

        Args:
            corpus (List[str]): A list of strings to train the tokenizer.
            save_output (bool): Saves the tokenizer output.
        """
        i = 0
        # Add [EOS] and [UNK] to encoder and decoder dicts
        self.words_to_i[self.eos_word] = i
        self.i_to_words[i] = self.eos_word
        i += 1
        self.words_to_i[self.unk_word] = i
        self.i_to_words[i] = self.unk_word
        i += 1

        for word in corpus:
            if word not in self.words_to_i.keys():
                self.words_to_i[word] = i
                self.i_to_words[i] = word
                i += 1

        self.vocab_size = i

        if save_path:
            self.save(save_path)

    def tokenize(self, corpus) -> list[int]:
        """Tokenize a dataset using a trained tokenizer.

        Args:
            corpus (List[str]): A list of strings to tokenize.

        Returns:
            tokenized_corpus (List[int]): A list of integers representing the tokenized corpus
        """
        tokenized_corpus = []

        for word in corpus:
            if word in self.words_to_i.keys():
                tokenized_corpus.append(self.words_to_i[word])
            else:
                tokenized_corpus.append(self.words_to_i[self.unk_word])

        return tokenized_corpus

    def enc(self, words: list[str]) -> list[int]:
        """Return list of ints from list of strings."""
        return [
            (
                self.words_to_i[word]
                if word in self.words_to_i.keys()
                else self.words_to_i[self.unk_word]
            )
            for word in words
        ]

    def dec(self, tokens: list[int]) -> list[str]:
        """Return list of strings from list of ints."""
        return [
            self.i_to_words[token] if token in self.i_to_words.keys() else self.unk_word
            for token in tokens
        ]
