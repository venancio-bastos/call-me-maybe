from enum import Enum, auto


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
    def __init__(self, prompt: str, schema_list: list) -> None:
        self.prompt = prompt
        self.schemas = schema_list
        self.current_state = JSONState.START
        self.choosen_function = None
        self.current_param = None
        self.text_buffer = ""
    
    def get_allowed_strings(self) -> list[str]:
        """
        Check the actual state and returns a list of allowed strings.
        """
        if self.current_state == JSONState.START:
            return ["[\n  {"]

        if self.current_state == JSONState.PROMPT_KEY:
            return ['\n    "prompt": "']

        if self.current_state == JSONState.PROMPT_VALUE:
            return [self.prompt]

        if self.current_state == JSONState.NAME_KEY:
            return ['",\n    "name": "']

        if self.current_state == JSONState.NAME_VALUE:
            return [schema.name for schema in self.schemas]

        if self.current_state == JSONState.PARAMS_KEY:
            return ['",\n    "parameters": {']

        if self.current_state == JSONState.PARAMS_VALUE:
            print(f"current_param: {self.current_param}")
            if self.current_param is None:
                print(f"choosen_function: {self.choosen_function}")
                if not self.choosen_function:
                    return []
                return [f'"{k}": ' for k in self.choosen_function.parameters.keys()]
            if self.current_param.type == "number":
                return ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "-", ",", "}"]
            return []

        if self.current_state == JSONState.END:
            return ["}  \n]"]
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
            if '"prompt": "' in self.text_buffer:
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
                for param_name, param_obj in self.choosen_function.parameters.items():
                    if f'"{param_name}": ' in self.text_buffer:
                        self.current_param = param_obj
                        self.text_buffer = ""
                        break
            else:
                if "," in self.text_buffer:
                    self.current_param = None
                    self.text_buffer = ""
                elif "}" in self.text_buffer:
                    self.current_state = JSONState.END
                    self.text_buffer = ""
