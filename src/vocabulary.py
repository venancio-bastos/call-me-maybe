import json
from typing import Dict


class Vocabulary:
    """
    Generates a map between tokens in text and its respectives numeric IDs.
    """
    def __init__(self, model_sdk) -> None:
        """
        Open and save vocabolary in ram.
        """
        vocab_path = model_sdk.get_path_to_vocab_file()

        with open(vocab_path, "r", encoding="utf-8") as f:
            self._vocab_dict: Dict[str, int] = json.load(f)

    def get_id_by_token(self, token_str: str) -> int:
        """
        Look for token in dict and return the ID.
        """
        if token_str in self._vocab_dict:
            return self._vocab_dict[token_str]
        raise KeyError(
            f"Error: The token {self._vocab_dict} don't exist in vocabulary"
        )

    def get_vocab_size(self) -> int:
        """
        Returns the len of vocabulary ( needed to validate logits size ).
        """
        return len(self._vocab_dict)
