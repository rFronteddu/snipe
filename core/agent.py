from core.memory import Memory
import yaml
import json
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Agent")
logging.getLogger("httpx").setLevel(logging.WARNING)

def _load_prompts():
    prompts = {}
    for p in ["planner", "agent", "direct", "memory"]:
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

    def get_tool_schemas(self):
        """Returns tool info in a format the LLM can easily parse (JSON-like)."""
        return [{"name": t.name, "description": t.description} for t in self.tools.values()]

    def handle_message(self, message_obj: str):
        """Main entry point for handling user messages with a plan-and-execute loop."""

        # 1. Extract the actual string content immediately
        # If your message object has a .content attribute, use that.
        # Otherwise, str(message_obj) is a safe fallback.
        user_text = getattr(message_obj, 'content', str(message_obj))

        # 2. Fetch Context (Summary + Recent Turns)
        history = self.memory.get_recent_context(limit=5)

        # 3. Planning (Requesting JSON specifically)
        plan_prompt = self.prompts["planner"].format(
            tools=json.dumps(self.get_tool_schemas()),
            history=history,
            user_input=user_text
        )

        plan_raw = self.llm.generate(plan_prompt)

        # PRINT REASONING: Show what the LLM decided to do
        print("\n" + "=" * 20 + " PLANNER OUTPUT " + "=" * 20)
        print(plan_raw)
        print("=" * 56 + "\n")

        plan = self._safe_parse_json(plan_raw)

        # todo should execute again until output is in valid json


        # 3. Execution Loop
        observations = []
        final_response = "The planner failed to provide a concluding response step."

        for step in plan.get("steps", []):
            step_type = step.get("type", "").lower()

            if step_type == "tool":
                tool_name = step.get("tool_name")
                tool_input = step.get("input", "")

                print(f"[ACTION] Using Tool: {tool_name} | Input: {tool_input}")

                result = self._exec_tool(tool_name, tool_input)
                observations.append({"step": tool_name, "result": result})

                print(f"[OBSERVATION] {result}\n")

            elif step_type == "respond":
                thought = step.get("thought", "Generating final response...")

                print(f"[THOUGHT] {thought}")

                # Final Synthesis: Hand off observations and history to Umberto
                final_response = self._finalize(
                    user_input=user_text,
                    observations=observations,
                    thought=thought,
                    history=history
                )
                break  # Exit loop once a response is generated

        # 5. Memory Management
        # Store the turn in history
        self.memory.add_chat_turn("user", user_text)
        self.memory.add_chat_turn("assistant", final_response)

        # Check if history is getting too long and condense it
        self.memory.summarize_if_needed(self.llm, self.prompts["memory"])

        return final_response

    def _exec_tool(self, name, tool_input):
        if name not in self.tools:
            return f"Error: Tool {name} not found."
        try:
            return self.tools[name].run(tool_input)
        except Exception as e:
            logger.error(f"Execution error for {name}: {e}")
            return f"Error executing {name}: {str(e)}"

    def _safe_parse_json(self, text):
        """Attempts to extract and parse JSON from LLM text."""
        try:
            # Flexible regex to find the JSON block even with LLM conversational fluff
            match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
            json_str = match.group(1) if match else text
            return json.loads(json_str)
        except (ValueError, json.JSONDecodeError, AttributeError):
            logger.error(f"Failed to parse plan JSON. Raw text: {text}")
            return {"steps": [{"type": "respond", "thought": "The planner failed to generate a valid JSON structure."}]}


    def _finalize(self, user_input, observations, thought, history):
        """
        Synthesizes the final response for the user based on tool results.
        """
        final_prompt = self.prompts["direct"].format(
            user_input=user_input,
            thought=thought,
            results=json.dumps(observations),
            history = history
        )

        return self.llm.generate(final_prompt)