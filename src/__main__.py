from llm_sdk import Small_LLM_Model
import numpy as np


def main() -> None:
    model = Small_LLM_Model()
    tokens_tensor = model.encode("What is the sum of 40 and 2?")
    tokens_list = tokens_tensor.tolist()[0]
    logist_list = np.array(model.get_logits_from_input_ids(tokens_list))
    print(f"tokens_list: {tokens_list}")
    print(f"logist_list: {logist_list}")


if __name__ == "__main__":
    main()
