import json
from typing import Dict, List
from pydantic import BaseModel


class FunctionParameter(BaseModel):
    """
    Represents the properties of individual parameters (ex: the type).
    """
    type: str


class FunctionSchema(BaseModel):
    """
    Represents a complete definition of a valid function.
    """
    name: str
    description: str
    parameters: Dict[str, FunctionParameter]
    returns: Dict[str, str]


def load_functions_schema(filepath: str) -> List[FunctionSchema]:
    """
    Reads json file and convert it into a FunctionSchema object.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    return [FunctionSchema(**item) for item in raw_data]
