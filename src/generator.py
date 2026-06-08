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
    final_json = []
    
    while grammar.current_state != JSONState.END:
        logits = np.array(model.get_logits_from_input_ids(input_tokens))
        

        allowed_strings = grammar.get_allowed_strings()

        # print(f"Allowed_strings: {allowed_strings}")

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
                        full_tokens = model.encode(target_string).tolist()[0]
                        prefix_tokens = model.encode(grammar.text_buffer).tolist()[0] if grammar.text_buffer else []
                        
                        idx = len(prefix_tokens)
                        if idx < len(full_tokens):
                            allowed_token_ids.append(full_tokens[idx])

            if allowed_token_ids:
                mask[allowed_token_ids] = False
            else:
                mask.fill(False)

        logits[mask] = -np.inf

        next_token_id = int(np.argmax(logits))
        next_token_str = model.decode([next_token_id])
        grammar.consume_token(next_token_str)
        final_json.append(next_token_id)
        # print(f"final_json: {final_json}")
        # print(f"Decode: \n{model.decode(final_json)}")

    return model.decode(final_json)