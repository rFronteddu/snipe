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

    # -------------------------
    # TOOL DESCRIPTION BLOCK
    # -------------------------

    def tool_prompt(self):
        """Generates the tool block for prompts."""
        return "\n".join(
            [f"- {t.name}: {t.description}" for t in self.tools.values()])

    # -------------------------
    # PLANNER STEP
    # -------------------------

    def plan(self, user_input):

        prompt = self.prompts["planner"].format(
            tool_prompt=self.tool_prompt(),
            user_input=user_input
        )

        response = self.llm.generate(prompt)

        print("\n==== PLANNER ====")
        print(response)
        print("=================\n")

        return response

    # -------------------------
    # TOOL CALL PARSER
    # -------------------------

    @staticmethod
    def parse_tool_call(text):

        # This finds both in one go, even if there are extra spaces/newlines
        pattern = r"TOOL:\s*(.*?)\s*INPUT:\s*(.*)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

        if match:
            tool = match.group(1).strip().lower()
            tool_input = match.group(2).strip()
            return tool, tool_input

        return None, None

    # -------------------------
    # MAIN MESSAGE HANDLER
    # -------------------------

    def handle_message(self, message):

        user_input = message.content

        # -------------------------
        # STEP 1: PLANNING
        # -------------------------

        plan = self.plan(user_input)

        if "1. direct" in plan.lower():

            prompt = self.prompts["direct"].format(
                tool_prompt=self.tool_prompt(),
                user_input=user_input
            )

            print("\n==== DIRECT ANSWER ====\n")

            return self.llm.generate(prompt)

        # -------------------------
        # STEP 2: REACT LOOP
        # -------------------------

        history = ""

        for step in range(10):

            prompt = self.prompts["agent"].format(
                tool_description=self.tool_prompt(),
                plan=plan,
                history=history,
                user_input=user_input
            )

            response = self.llm.generate(prompt)

            print("\n==== ReAct Loop Response ====")
            print(response)
            print("======================\n")

            tool_name, tool_input = self.parse_tool_call(response)

            # -------------------------
            # TOOL EXECUTION
            # -------------------------

            if tool_name and tool_name in self.tools:

                tool = self.tools[tool_name]
                print(f"[TOOL CALL] {tool_name}({tool_input})")

                result = tool.run(tool_input)

                print(f"[TOOL RESULT] {result}\n")

                history += f"""
                Action: {tool_name}
                Input: {tool_input}
                Observation: {result}
                """
                continue

                # -------------------------
                # FINAL ANSWER
                # -------------------------

            print("\n==== FINAL ANSWER ====\n")

            return response

        return "Error: Maximum execution steps exceeded."
