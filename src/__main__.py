from llm_sdk.llm_sdk import Small_LLM_Model


def main() -> None:
    model = Small_LLM_Model()
    tokens = model.encode("Olá, tudo bem?")
    print(tokens)


if __name__ == "__main__":
    main()