# core/agent.py
from core.memory import Memory

class Agent:
    def __init__(self, tools, llm=None, memory_file="data/memory.json"):
        self.tools = tools
        self.llm = llm
        self.memory = Memory(memory_file)

    def tool_prompt(self):
        tool_descriptions = []
        for name, tool in self.tools.items():
            if name != "list_tools":  # optional
                tool_descriptions.append(f"{name}: {tool.description}")
        return "\n".join(tool_descriptions)

    def build_planner_prompt(self, user_input):
        return f"""
    You are an AI planner.

    Your job is to decide how to answer the user's request.

    Available tools:
    {self.tool_prompt()}

    If tools are needed, respond:

    PLAN: USE_TOOLS

    If the question can be answered directly, respond:

    PLAN: DIRECT_ANSWER

    User: {user_input}
    """

    def plan(self, user_input):
        planner_prompt = self.build_planner_prompt(user_input)

        planner_response = self.llm.generate(planner_prompt)

        print("\n==== PLANNER ====")
        print(planner_response)
        print("=================\n")

        if "USE_TOOLS" in planner_response:
            return "tools"

        return "direct"

    def build_prompt(self, user_input, history):
        return f"""You are an AI agent.
        You can use tools.
        Available tools:{self.tool_prompt()}
        When you want to use a tool respond EXACTLY like:
        TOOL: tool_name
        INPUT: tool_input
        Otherwise respond with the final answer.
        Conversation:
{history}
User: {user_input}
"""

    @staticmethod
    def parse_tool_call(text):

        if "TOOL:" not in text:
            return None, None

        lines = text.splitlines()

        tool_name = None
        tool_input = ""

        for line in lines:
            if line.startswith("TOOL:"):
                tool_name = line.replace("TOOL:", "").strip()

            if line.startswith("INPUT:"):
                tool_input = line.replace("INPUT:", "").strip()

        return tool_name, tool_input

    def handle_message(self, message):
        user_input = message.content

        # STEP 1 — planner
        plan = self.plan(user_input)

        if plan == "direct":
            prompt = f"""
            You are an AI assistant.

            A planner has already analyzed the user request and decided that
            you should answer the question directly without using tools.

            Answer the user's question clearly and helpfully. You still know about the available tools and can describe them if needed.
            
            Available tools:
            {self.tool_prompt()}
            User: {user_input}
            """
            return self.llm.generate(prompt)

        # STEP 2 — tool execution loop
        history = ""

        for step in range(10):  # max tool steps
            prompt = self.build_prompt(user_input, history)

            llm_response = self.llm.generate(prompt)

            # Print LLM response for this step
            print("\n==== LLM Response ====")
            print(llm_response)
            print("======================\n")

            tool_name, tool_input = self.parse_tool_call(llm_response)

            if tool_name and tool_name in self.tools:
                result = self.tools[tool_name].run(tool_input)

                history += f"""
                Tool used: {tool_name}
                Tool input: {tool_input}
                Tool result: {result}"""

                # print interaction
                print("\n==== Tool Used ====")
                print(f"Tool: {tool_name}")
                print(f"Input: {tool_input}")
                print(f"Output: {result}")
                print("==================\n")
                continue

            # LLM produced a final answer
            return llm_response

        return "Agent stopped after too many steps."