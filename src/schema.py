import json
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class FunctionParameter:
    """
    Represents the properties of individual parameters (ex: the type).
    """
    type: str


@dataclass
class FunctionSchema:
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

    schemas = []
    for item in raw_data:
        parsed_params = {}
        for param_name, param_info in item["parameters"].items():
            parsed_params[param_name] = FunctionParameter(
                type=param_info["type"]
            )

        schema = FunctionSchema(
            name=item["name"],
            description=item["description"],
            parameters=parsed_params,
            returns=item["returns"],
        )
        schemas.append(schema)

    return schemas
