import os
import json
import argparse
from llm_sdk import Small_LLM_Model
from src.generator import generate_json
from src.schema import load_functions_schema


def main() -> None:
    parser = argparse.ArgumentParser(description="Call Me Maybe - Constrained Decoding Pipeline")
    parser.add_argument(
        "--functions_definition", 
        default="data/input/functions_definition.json",
        help="Path to the functions definition file"
    )
    parser.add_argument(
        "--input", 
        default="data/input/function_calling_tests.json",
        help="Path to the input batch prompts file"
    )
    parser.add_argument(
        "--output", 
        default="data/output/function_calling_results.json",
        help="Path to save the generated JSON array"
    )
    args = parser.parse_args()

    if not os.path.exists(args.functions_definition):
        print(f"Error: Schema file {args.functions_definition} not found.")
        return
    schemas = load_functions_schema(args.functions_definition)

    if not os.path.exists(args.input):
        print(f"Error: Input file target {args.input} not found.")
        return

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            test_cases = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Input file {args.input} contains malformed JSON markup.")
        return

    print("Initializing LLM (Qwen) infrastructure...")
    model = Small_LLM_Model()
    
    results_array = []

    print(f"\nProcessing {len(test_cases)} prompts from input catalog...")
    for idx, item in enumerate(test_cases, start=1):
        prompt_string = item.get("prompt")
        if not prompt_string:
            print(f"Skipping index {idx}: Key 'prompt' is missing.")
            continue

        print(f"[{idx}/{len(test_cases)}] Generating constrained schema call for: '{prompt_string}'")
        raw_json_output = generate_json(model=model, prompt=prompt_string, schemas=schemas)
        
        try:
            parsed_object = json.loads(raw_json_output)

            func_name = parsed_object.get("name")
            params = parsed_object.get("parameters", {})

            matching_schema = next((s for s in schemas if s.name == func_name), None)
            if matching_schema and isinstance(params, dict):
                for param_name, val in params.items():
                    if param_name in matching_schema.parameters:
                        expected_type = matching_schema.parameters[param_name].type
                        
                        if expected_type == "number" and isinstance(val, (int, float)):
                            params[param_name] = float(val)
                        
                        elif expected_type == "integer" and isinstance(val, (int, float)):
                            params[param_name] = int(val)

            results_array.append(parsed_object)
        except Exception as parse_error:
            print(f"Warning: Output string failed structural parsing checks: {parse_error}")

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as out_file:
        json.dump(results_array, out_file, indent=2)

    print(f"\n--- EXECUTION FINISHED: Results written to {args.output} ---")


if __name__ == "__main__":
    main()