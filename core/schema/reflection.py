REFLECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {
            "type": "string",
            "enum": ["continue", "respond"]
        },
        "reason": {"type": "string"},
        "next_step": {
            "type": "object",
            "properties": {
                "type": {"enum": ["tool", "respond"]},
                "tool_name": {"type": "string"},
                "input": {"type": "object"},
                "thought": {"type": "string"}
            }
        }
    },
    "required": ["decision"]
}