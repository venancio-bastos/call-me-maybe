import os
from llm_sdk import Small_LLM_Model
from src.generator import generate_json
from src.schema import load_functions_schema


def main() -> None:
    schema_path = "functions_definition.json"

    if not os.path.exists(schema_path):
        print(f"Error: File {schema_path} was not found")
        return

    print("Loading functions definitions")
    schemas = load_functions_schema(schema_path)

    print("Initializing LLM (Qwen) model...")
    model = Small_LLM_Model()

    prompt_teste = "What is the sum of 2 and 3?"
    print(f"\nPrompt enviado: '{prompt_teste}'")

    json_final = generate_json(model=model, prompt=prompt_teste, schemas=schemas)

    print("\n--- JSON GERADO COM SUCESSO ---")
    print(json_final)


if __name__ == "__main__":
    main()
