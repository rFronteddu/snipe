PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["tool", "respond"]
                    },
                    "tool_name": {"type": "string"},
                    "input": {"type": "object"},
                    "thought": {"type": "string"}
                },
                "required": ["type"]
            }
        }
    },
    "required": ["steps"]
}