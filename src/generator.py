from typing import List, Any
import numpy as np
from src.grammar import JSONGrammar, JSONState
from src.schema import FunctionSchema
from src.vocabulary import Vocabulary


def generate_json(model: Any, prompt: str, schemas: List[FunctionSchema]) -> str:
    """
    Execute the main constrained decoding loop to generate a valid JSON.
    """
    try:
        vocab = Vocabulary(model)
        grammar = JSONGrammar(prompt=prompt, schema_list=schemas)

        initial_tokens: List[int] = model.encode(prompt).tolist()[0]
        input_tokens: List[int] = list(initial_tokens)
        final_json: List[int] = []        

        while grammar.current_state != JSONState.END:
            # print(f"Buffer: {grammar.text_buffer}")
            logits = np.array(model.get_logits_from_input_ids(input_tokens))

            allowed_strings = grammar.get_allowed_strings()
            
            vocab_size = logits.shape[0]
            mask = np.ones(vocab_size, dtype=bool)
            allowed_token_ids = []

            if len(allowed_strings) == 0:
                mask.fill(False)
            else:
                for string in allowed_strings:
                    token = model.encode(string).tolist()[0]
                    # print(f"Token: {token} | Token decode: {model.decode(token)} | String: {string}")

                    if string.startswith(grammar.text_buffer):
                        full_token = model.encode(string).tolist()[0]
                        text_buffer_token = model.encode(grammar.text_buffer).tolist()[0]

                        idx = len(text_buffer_token)

                        if idx < len(full_token):
                            allowed_token_ids.append(full_token[idx])

                        if allowed_token_ids:
                            mask[allowed_token_ids] = False
                        else:
                            mask.fill(False)
                
            logits[mask] = -np.inf
            next_token_id = np.argmax(logits)
            next_token_str = model.decode(next_token_id)
            # print(f"next_token_str: {next_token_str}")
            grammar.consume_token(next_token_str)
            final_json.append(next_token_id)


            # print(f"Final Json: \n{model.decode(final_json)}")
        return model.decode(final_json)
    except Exception as e:
        # print(f"Error during JSON generation pipeline: {e}")
        return "{}"