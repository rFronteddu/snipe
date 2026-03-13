from core.memory import Memory
import yaml
import re

class Agent:
    def __init__(self, tools, llm=None, memory_file="data/memory.json"):
        # load all provisioned prompts
        self.prompts = {}
        for p in ["planner", "agent", "direct"]:
            with open(f"prompts/v1/{p}.yaml", "r") as f:
                self.prompts[p] = yaml.safe_load(f)["template"]

        self.tools = tools
        self.llm = llm
        self.memory = Memory(memory_file)

    def tool_prompt(self):
        """Generates the tool block for the LLM instructions."""
        return "\n".join([f"- {t.name}: {t.description}" for t in self.tools.values()])

    def plan(self, user_input):
        prompt = self.prompts["planner"].format(
            tool_prompt=self.tool_prompt(),
            user_input=user_input
        )
        response = self.llm.generate(prompt)

        print("\n==== PLANNER ====")
        print(response)
        print("=================\n")

        # Simple but effective intent check
        return "tools" if "USE_TOOLS" in response else "direct"

    @staticmethod
    def parse_tool_call(text):
        # This finds both in one go, even if there are extra spaces/newlines
        pattern = r"TOOL:\s*(.*?)\s*INPUT:\s*(.*)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

        if match:
            # HERE you would use .group(1) and .group(2)
            return match.group(1).strip(), match.group(2).strip()
        return None, None

    def handle_message(self, message):
        user_input = message.content

        # STEP 1 — planner
        intent = self.plan(user_input)
        if intent == "direct":
            prompt = self.prompts["direct"].format(
                tool_prompt=self.tool_prompt(),
                user_input=user_input
            )
            return self.llm.generate(prompt)

        # ReAct Loop (Step 2)
        history = ""
        for _ in range(10):  # max tool steps
            prompt = self.prompts["agent"].format(
                tool_description=self.tool_prompt(),
                history=history,
                user_input=user_input
            )

            response = self.llm.generate(prompt)

            # Print LLM response for this step
            print("\n==== ReAct Loop Response ====")
            print(response)
            print("======================\n")

            tool_name, tool_input = self.parse_tool_call(response)

            if tool_name in self.tools:
                result = self.tools[tool_name].run(tool_input)

                # Record what the agent said AND what the tool returned
                history += f"\nAgent: {response}\nObservation: {result}"

                print(f"[*] Tool {tool_name} returned: {result}")
                continue

            # no more tool calls detected? Treat as final answer
            return response

        return "Error: Maximum execution steps exceeded."