import numpy as np
from src.grammar import JSONGrammar, JSONState
from src.vocabulary import Vocabulary


def generate_json(model, prompt: str, schemas: list) -> str:
    """
    Main loop to generate json.
    """
    vocab = Vocabulary(model)
    grammar = JSONGrammar(prompt=prompt, schema_list=schemas)

    input_tokens = model.encode(prompt).tolist()[0]

    while grammar.current_state != JSONState.END:
        logits = np.array(model.get_logits_from_input_ids(input_tokens))

        allowed_strings = grammar.get_allowed_strings()

        vocab_size = logits.shape[0]
        mask = np.ones(vocab_size, dtype=bool)

        allowed_token_ids = []
        if len(allowed_strings) == 0:
            mask.fill(False)
        else:
            for target_string in allowed_strings:
                if target_string.startswith(grammar.text_buffer):
                    remainder = target_string[len(grammar.text_buffer) :]

                    if remainder:
                        remainder_tokens = model.encode(remainder).tolist()[0]
                        allowed_token_ids.append(remainder_tokens[0])

            if allowed_token_ids:
                mask[allowed_token_ids] = False
            else:
                mask.fill(False)

        logits[mask] = -np.inf

        next_token_id = int(np.argmax(logits))
        next_token_str = model.decode([next_token_id])
        grammar.consume_token(next_token_str)
        input_tokens.append(next_token_id)

    return model.decode(input_tokens)