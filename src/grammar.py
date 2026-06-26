import json
from enum import Enum, auto
from typing import List, Optional
from src.schema import FunctionSchema, FunctionParameter


class JSONState(Enum):
    """
    Explicit list with all the possible states for the JSON grammar.
    """
    START = auto()
    PROMPT_KEY = auto()
    PROMPT_VALUE = auto()
    NAME_KEY = auto()
    NAME_VALUE = auto()
    PARAMS_KEY = auto()
    PARAMS_VALUE = auto()
    END = auto()
    FINISHED = auto()


class JSONGrammar:
    """
    Manages the JSON generation state and determines which characters are permitted.
    """
    def __init__(self, prompt: str, schema_list: List[FunctionSchema]) -> None:
        # Safely escape quotes and backslashes in the user prompt to prevent JSON breakage
        self.prompt: str = json.dumps(prompt)[1:-1]
        self.schemas: List[FunctionSchema] = schema_list
        self.current_state: JSONState = JSONState.START
        self.choosen_function: Optional[FunctionSchema] = None
        self.current_param: Optional[FunctionParameter] = None
        self.filled_parameters: List[str] = []
        self.text_buffer: str = ""

    def _is_string_closed(self, text: str) -> bool:
        """
        Checks if a JSON string value is fully closed, 
        ignoring escaped internal quotes (\").
        """
        if not text.startswith('"'):
            return False
        
        escaped = False
        for i in range(1, len(text)):
            char = text[i]
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                return True # Found the actual closing quote
        return False

    def get_allowed_strings(self) -> list[str]:
        """
        Checks the current state and returns a list of allowed strings.
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
            remain = [k for k in self.choosen_function.parameters.keys() if k not in self.filled_parameters]

            if self.current_param is None:
                if not remain:
                    return ["}"]
                else:
                    return [f'"{remain[0]}": ']
            else:
                # 1. Number and Integer validation
                if self.current_param.type in ["number", "integer"]:
                    if self.text_buffer == "":
                        return ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-"]
                    
                    allowed_chars = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
                    
                    # Decimals are only allowed for strictly "number" types, not "integer"
                    if self.current_param.type == "number" and "." not in self.text_buffer:
                        allowed_chars.append(".")
                    
                    allowed_strings = [self.text_buffer + c for c in allowed_chars]
                    
                    if self.text_buffer[-1] not in ["-", "."]:
                        if remain:
                            allowed_strings.append(self.text_buffer + ",")
                        else:
                            allowed_strings.append(self.text_buffer + "}")
                    return allowed_strings
            
                # 2. Boolean validation
                elif self.current_param.type == "boolean":
                    if remain:
                        return ["true,", "false,"]
                    else:
                        return ["true}", "false}"]
                
                # 3. String validation
                elif self.current_param.type == "string":
                    # Force opening quote if missing
                    if not self.text_buffer.startswith('"'):
                        return ['"']
                    
                    # Once closed, enforce the next structural delimiter
                    if self._is_string_closed(self.text_buffer):
                        if remain:
                            return [self.text_buffer + ","]
                        else:
                            return [self.text_buffer + "}"]
                    
                    # Yield empty list to allow the model to freely generate string content
                    return []
                    
        if self.current_state == JSONState.END:
            return ["\n}"]
        
        return []
    
    def consume_token(self, token_str: str) -> None:
        """
        Consumes the generated token, updates the buffer, 
        and manages syntax state transitions.
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
            if self.current_param is None:
                # Look for the next parameter key
                for param_name, param_obj in self.choosen_function.parameters.items():
                    expected_key = f'"{param_name}": '
                    if expected_key in self.text_buffer:
                        self.current_param = param_obj
                        self.filled_parameters.append(param_name)
                        self.text_buffer = ""
                        break
            else:
                # Se for string, só procuramos delimitadores APÓS a aspa de fecho
                if self.current_param.type == "string":
                    if self._is_string_closed(self.text_buffer):
                        # Encontra a posição da aspa de fecho real
                        # (O teu _is_string_closed já é bom, vamos apenas isolar o que vem depois)
                        last_quote = self.text_buffer.rfind('"')
                        after_string = self.text_buffer[last_quote+1:]
                        
                        if ',' in after_string:
                            self.current_param = None
                            self.text_buffer = ""
                        elif '}' in after_string:
                            remain = [k for k in self.choosen_function.parameters.keys() if k not in self.filled_parameters]
                            if not remain:
                                self.current_state = JSONState.END
                                self.text_buffer = ""
                else:
                    # Para números e booleanos, o teu código original está ótimo
                    if ',' in self.text_buffer:
                        self.current_param = None
                        self.text_buffer = ""
                    elif '}' in self.text_buffer:
                        remain = [k for k in self.choosen_function.parameters.keys() if k not in self.filled_parameters]
                        if not remain:
                            self.current_state = JSONState.END
                            self.text_buffer = ""

        elif self.current_state == JSONState.END:
            if "}" in self.text_buffer:
                self.current_state = JSONState.FINISHED
                self.text_buffer = ""