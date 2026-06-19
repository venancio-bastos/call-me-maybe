from enum import Enum, auto
from typing import List, Optional, Any
from src.schema import FunctionSchema, FunctionParameter


class JSONState(Enum):
    """
    Explicit list with all the possible states for JSON grammar.
    """
    START = auto()
    PROMPT_KEY = auto()
    PROMPT_VALUE = auto()
    NAME_KEY = auto()
    NAME_VALUE = auto()
    PARAMS_KEY = auto()
    PARAMS_VALUE = auto()
    END = auto()


class JSONGrammar:
    """
    Manage the json generate state abd tell wich caracters are permitted.
    """
    def __init__(self, prompt: str, schema_list: List[FunctionSchema]) -> None:
        self.prompt: str = prompt
        self.schemas: List[FunctionSchema] = schema_list
        self.current_state: JSONState = JSONState.START
        self.choosen_function: Optional[FunctionSchema] = None
        self.current_param: Optional[FunctionParameter] = None
        self.filled_parameters: List[str] = []
        self.text_buffer: str = ""

    def get_allowed_strings(self) -> list[str]:
        """
        Check the actual state and returns a list of allowed strings.
        """
        if self.current_state == JSONState.START:
            return ["{\n"]

        if self.current_state == JSONState.PROMPT_KEY:
            return ['    "prompt": "']

        if self.current_state == JSONState.PROMPT_VALUE:
            return [self.prompt]

        if self.current_state == JSONState.NAME_KEY:
            return ['",\n    "name": "']

        if self.current_state == JSONState.NAME_VALUE:
            return [schema.name for schema in self.schemas]

        if self.current_state == JSONState.PARAMS_KEY:
            return ['",\n    "parameters": {']

        if self.current_state == JSONState.PARAMS_VALUE:
            remain = []
            for k in self.choosen_function.parameters.keys():
                if k not in self.filled_parameters:
                    remain.append(k)

            if self.current_param == None:
                if not remain:
                    return ["}"]
                else:
                    allowed_keys = []
                    for k in remain:
                        allowed_keys.append(f'"{k}"')
                    return allowed_keys
            else:
                allowed = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-", "."]
                
                if self.current_param.type == "number":
                    if remain:
                        allowed.append(",\n    ")
                    else:
                        allowed.append("\n    }")
            return allowed

        if self.current_state == JSONState.END:
            return ["\n}"]
        return []
    
    def consume_token(self, token_str: str) -> None:
        """
        Consume the generated token, update the buffer and
        change syntax state
        """
        self.text_buffer += token_str

        if self.current_state == JSONState.START:
            if "{" in self.text_buffer:
                self.current_state = JSONState.PROMPT_KEY
                self.text_buffer = ""

        elif self.current_state == JSONState.PROMPT_KEY:
            if '    "prompt": "' in self.text_buffer:
                self.current_state = JSONState.PROMPT_VALUE
                self.text_buffer = ""

        elif self.current_state == JSONState.PROMPT_VALUE:
            if self.prompt in self.text_buffer:
                self.current_state = JSONState.NAME_KEY
                self.text_buffer = ""

        elif self.current_state == JSONState.NAME_KEY:
            if '"name": "' in self.text_buffer:
                self.current_state = JSONState.NAME_VALUE
                self.text_buffer = ""

        elif self.current_state == JSONState.NAME_VALUE:
            for schema in self.schemas:
                if schema.name in self.text_buffer:
                    self.choosen_function = schema
                    self.current_state = JSONState.PARAMS_KEY
                    self.text_buffer = ""
                    break

        elif self.current_state == JSONState.PARAMS_KEY:
            if '"parameters": {' in self.text_buffer:
                self.current_state = JSONState.PARAMS_VALUE
                self.text_buffer = ""

        elif self.current_state == JSONState.PARAMS_VALUE:
            if self.current_param == None:
                for param_name, param_obj in self.choosen_function.parameters.items():
                    expected_key = f'"{param_name}"'

                    if expected_key in self.text_buffer:
                        self.current_param = param_obj
                        self.filled_parameters.append(expected_key)
                        self.text_buffer = ""
                        break
            else:
                if ',' in self.text_buffer:
                    self.current_param = None
                    self.text_buffer = ""
                elif "}" in self.text_buffer:
                    self.current_state = JSONState.END
                    self.text_buffer = ""

