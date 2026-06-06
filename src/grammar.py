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
            return ["{"]
        if self.current_state == JSONState.PROMPT_KEY:
            return ['"\n  "prompt": "']
        if self.current_state == JSONState.PROMPT_VALUE:
            return []
        if self.current_state == JSONState.NAME_KEY:
            return ['", \n  "name": "']
        if self.current_state == JSONState.NAME_VALUE:
            return [schema.name for schema in self.schemas]
        if self.current_state == JSONState.PARAMS_KEY:
            if not self.choosen_function:
                return []
            return list(self.choosen_function.parameters.keys())
        if self.current_state == JSONState.PARAMS_VALUE:
            if self.current_state and self.current_param.type == "number":
                return ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "-", ",", "}"]
            return []
        if self.current_state == JSONState.END:
            return ["}"]
        return []
    
    def consume_token(self, token_str: str) -> None:
        """
        Consume the generated token, update the buffer and
        change sintaxe state
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
            if "}" in self.text_buffer and self.text_buffer.count("}") >= 2:
                self.current_state = JSONState.END
                self.text_buffer = ""


if __name__ == "__main__":
    # Simulação rápida sem IA para ver se os estados avançam
    from src.schema import FunctionSchema
    
    # Criamos um schema falso apenas para teste
    mock_schema = FunctionSchema(
        name="fn_add_numbers",
        description="test",
        parameters={},
        returns={}
    )
    
    grammar = JSONGrammar(prompt="Somar 2 e 3", schema_list=[mock_schema])
    
    # Sequência de tokens simulados que a IA geraria
    tokens_simulados = [
        "{", 
        '"\n  "prompt": "', 
        "Somar 2 e 3", 
        '",\n  "name": "', 
        "fn_add_numbers", 
        '",\n  "parameters": {'
    ]
    
    print("--- Teste de Transição de Estados ---")
    for token in tokens_simulados:
        estado_anterior = grammar.current_state
        grammar.consume_token(token)
        print(f"Recebeu: {repr(token)} | Estado: {estado_anterior.name} -> {grammar.current_state.name}")