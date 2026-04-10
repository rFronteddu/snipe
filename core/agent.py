import re

from core.memory import Memory
import yaml
import json
import logging
from jsonschema import validate, ValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Agent")
logging.getLogger("httpx").setLevel(logging.WARNING)


def _load_prompts():
    prompts = {}
    for p in ["planner", "direct", "memory"]:
        try:
            with open(f"prompts/v1/{p}.yaml", "r") as f:
                prompts[p] = yaml.safe_load(f)["template"]
        except FileNotFoundError:
            logger.error(f"Prompt file {p}.yaml missing.")
    return prompts


class Agent:
    def __init__(self, tools, llm=None, memory_file="data/memory.json"):
        self.memory = Memory(memory_file)
        self.tools = tools
        self.llm = llm
        self.prompts = _load_prompts()

        # Export tool schemas for the planner
        self.tool_schemas = [tool.schema() for tool in self.tools.values()]

    def handle_message(self, message_obj: str, max_memory_recall=5, max_retries=3, max_plan_steps=10):
        """
        Main entry point for handling user messages using
        a plan → execute → respond loop.
        """

        user_text = getattr(message_obj, 'content', str(message_obj))
        history = self.memory.get_recent_context(limit=max_memory_recall)

        # Planning Loop

        last_error = None
        plan = None

        plan_prompt_template = self.prompts["planner"]

        for attempt in range(1, max_retries + 1):
            plan_prompt = plan_prompt_template.format(
                tools=json.dumps(self.tool_schemas, indent=2),
                history=history,
                user_input=user_text,
                last_error=last_error or ""
            )

            plan_raw = self.llm.generate(plan_prompt)
            logger.info(f"\n=== PLANNER OUTPUT (attempt {attempt}) ===\n{plan_raw}\n")

            plan, error = self._safe_parse_json(plan_raw)

            if plan and isinstance(plan.get("steps"), list):
                break
            last_error = f"JSON parse error: {error}"

        # Fallback if planner fails completely
        if not plan or "steps" not in plan:
            plan = {"steps": [
                {"type": "respond", "thought": "The planner failed to generate a valid plan."}]}

        # Execution Loop
        observations = []
        final_response = ""

        for step in plan.get("steps", [])[:max_plan_steps]:
            step_type = step.get("type", "").lower()

            if step_type == "tool":
                tool_name = step.get("tool_name")
                params = step.get("input", {})

                logger.info(f"[ACTION] Tool: {tool_name} | Input: {params}")

                result = self._exec_tool(tool_name, params)

                observations.append({"tool": tool_name, "input": params, "result": result})
                logger.info(f"[OBSERVATION] {result}")

            elif step_type == "respond":
                thought = step.get("thought") or "Use tool results to answer directly."
                logger.info(f"[THOUGHT] {thought}")

                # Hand off observations and history to Umberto
                final_response = self._finalize(
                    user_input=user_text,
                    observations=observations,
                    thought=thought,
                    history=history
                )
                break  # Exit loop once a response is generated

        # Memory Management

        self.memory.add_chat_turn("user", user_text)
        self.memory.add_chat_turn("assistant", final_response)

        # Condense memory if too long
        self.memory.summarize_if_needed(self.llm, self.prompts["memory"])

        return final_response

    # Tool Execution
    def _exec_tool(self, name, params):
        if name not in self.tools:
            return f"Error: Tool {name} not found."

        tool = self.tools[name]

        try:
            validate(instance=params, schema=tool.input_schema)
        except ValidationError  as e:
            logger.error(f"Validation error for {name}: {e}")
            return f"Tool input validation error: {e.message}"
        try:
            return tool.run(params)
        except Exception as e:
            logger.error(f"Execution error for {name}: {e}")
            return f"Tool execution error: {str(e)}"

    # JSON parsing
    def _extract_json(self, text):
        """
        Extract the first JSON object from LLM output.
        """
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return match.group(0) if match else None

    def _safe_parse_json(self, text):
        """
        Attempts to extract and parse JSON from LLM output.
        Returns (json_obj, error_message).
        """

        try:
            json_str = self._extract_json(text)
            if not json_str:
                return None, "No JSON object found."
            return json.loads(json_str), None

        except Exception as e:
            logger.error(f"Failed to parse plan JSON. Raw text: {text}")
            return None, str(e)

    # Final Response Generation
    def _finalize(self, user_input, observations, thought, history):
        """
        Synthesizes the final user-facing response.
        """

        final_prompt = self.prompts["direct"].format(
            user_input=user_input,
            thought=thought,
            results=json.dumps([o["result"] for o in observations], indent=2),
            history=history
        )

        return self.llm.generate(final_prompt)
