*This project has been created as part of the 42 curriculum by \<vebastos\>.*

# Call Me Maybe

## Description

**Call Me Maybe** is a function calling system that translates natural language prompts into structured, schema-compliant function calls using a small local LLM (Qwen3-0.6B). Given a prompt like `"What is the sum of 2 and 3?"`, it does not return `5` — instead it produces:

```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": {
    "a": 2.0,
    "b": 3.0
  }
}
```

The core challenge is reliability: a 0.6B parameter model is notoriously unreliable at producing structured output when prompted freely. This project solves that using **constrained decoding** — a technique that intercepts the model's token generation at each step, masking any token that would break the target schema, guaranteeing 100% valid and parseable JSON output regardless of prompt complexity.



## Instructions

### Requirements

- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv) package manager
- The `llm_sdk/` package (copy it to the project root alongside `src/`)

### Installation

#### Before instalation on 42 campus
```bash
export UV_CACHE_DIR=~/sgoinfre/uv_cache
export UV_PROJECT_ENVIRONMENT=~/sgoinfre/venv
export TRANSFORMERS_CACHE=/sgoinfre/vebastos/huggingface
export HF_HOME=/sgoinfre/vebastos/huggingface
```
###
```bash
make install
```

This runs `uv sync`, which creates a virtual environment and installs all dependencies from `pyproject.toml`.

### Running the project

```bash
make run
```

Or with explicit paths:

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

All three arguments are optional — the paths above are the defaults.

### Other Makefile targets

```bash
make lint           # flake8 + mypy with standard flags
make lint-strict    # flake8 + mypy --strict
make debug          # Run with Python's built-in debugger (pdb)
make clean          # Remove __pycache__ and .mypy_cache
make fclean         # Remove .llm, .uv_cache and .venv
```


## Algorithm Explanation

The core algorithm implements a Constrained Decoding approach via a Finite State Machine (FSM). The JSON grammar is mapped strictly to distinct states (START, PROMPT_KEY, NAME_VALUE, PARAMS_KEY, PARAMS_VALUE, END, FINISHED). At every decoding step, the FSM generates a list of exact strings allowed at that precise moment. The engine encodes these strings into tokens, creates a boolean mask over the model's entire vocabulary space, and sets the probabilities (logits) of all unapproved tokens to -np.inf. Finally, the model computes np.argmax(logits) over the masked array, forcing it to predict the most likely token only from the mathematically permitted pool.

## Design Decisions

The engine logic was completely decoupled by splitting the FSM tracker (grammar.py) and the generative loop (generator.py), preventing the code from becoming a monolithic block. Prioritized algorithmic purity, utilizing a strict keyword-based routing logic within the system context instead of unstable few-shot prompting to force the LLM to adhere to the schema. Additionally, to prevent the tokenizer from merging structural delimiters like quotes and braces with data, it was implemented an anchor-based string freezing logic that ensures structural stability.

## Performance Analysis

Tested on the provided `function_calling_tests.json` (11 prompts, CPU hardware):

| Category | Accuracy |
|---|---|
| Function name selection | ~100% |
| Number extraction | ~100% |
| Simple string extraction | ~95% |
| Multi-parameter / regex inference | ~90% |

**JSON validity**: 100% — every output is parseable and schema-compliant by construction.

**Speed**: all 11 prompts processed in under 4~ minute on standard CPU hardware.

The main accuracy limitation is the 0.6B model's ability to infer implicit values from ambiguous prompts (e.g. deriving a regex pattern from a natural language description). Values explicitly stated in the prompt are extracted correctly in nearly all cases.



## Challenges Faced

**Infinite number loops** — the number generator accumulated digits indefinitely (e.g. `2.000000...`) because the model preferred extending decimal places. Fixed by rejecting tokens that produce `nan` or `inf` and by neutralising pure whitespace tokens.

**BPE space markers** — the tokenizer prefixes space-bearing tokens with `Ġ`. Stripping it naively removed whitespace from multi-word strings. Fixed by converting `Ġ` to a real space only when the current accumulated value is non-empty.

**Multi-parameter positional confusion** — for prompts like `"What is the sum of 2 and 3?"`, the model tended to compute the result (`5`) instead of extracting both operands separately. Fixed by the progressive context accumulation strategy, which shows `a=2.0\nb=` before the model generates `b`.

**Wrong function selection for edge cases** — early versions confused regex substitution with template formatting on prompts mentioning placeholders. Addressed via the `it_match` semantic validator.



## Testing Strategy

- End-to-end runs with the provided `function_calling_tests.json` after each significant change.
- Visual inspection of the output JSON for schema compliance (correct keys, correct types, no extra fields).
- Edge cases tested: multi-parameter functions, strings with spaces and quotes, large numbers, scientific notation, regex patterns, boolean values.
- Output compared against expected results to catch regressions during refactoring.



## Example Usage

```bash
# Run with default paths
make run

# Run with explicit paths
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

Example output (`data/output/function_calling_results.json`):

```json
[
  {
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": { "a": 2.0, "b": 3.0 }
  },
  {
    "prompt": "Greet shrek",
    "name": "fn_greet",
    "parameters": { "name": "shrek" }
  },
  {
    "prompt": "Reverse the string 'hello'",
    "name": "fn_reverse_string",
    "parameters": { "s": "hello" }
  }
]
```

## Resources

- [Qwen3 Model Card](https://huggingface.co/Qwen/Qwen3-0.6B) - the LLM used in this project
- [Softmax Activation Function in Neural Networks](https://www.geeksforgeeks.org/deep-learning/the-role-of-softmax-in-neural-networks-detailed-explanation-and-applications/) - used to understand softmax probability calculation for valid token selection
- [Pydantic documentation](https://docs.pydantic.dev/) - used for all input validation
- [HuggingFace NLP Course - BPE Tokenization](https://huggingface.co/learn/nlp-course/chapter6/5) - background on how `Ġ` space markers work in BPE vocabularies
- [Gemini](https://gemini.google.com/) - Used as a pair-programming and debugging assistant to analyze terminal logs, pinpoint the BPE Tokenizer Fusion bug, brainstorm structural refactoring of some methods, and draft the FSM logic mapping.
### AI Usage

AI was used to clarify how the Qwen tokenizer encodes specific characters (e.g. `=`, `:`, `Ġ`, `Ċ`), to understand the structure of the vocabulary JSON file, and to refine docstrings and inline comments throughout the codebase.