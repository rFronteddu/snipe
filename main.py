from core.agent import Agent
from tools.registry import load_tools
from core.llm import OllamaLLM
from channels.terminal_channel import UserTerminalChannel

class Message:
    def __init__(self, content):
        self.content = content

def main():
    llm = OllamaLLM(model="llama3.2:latest", host="http://10.100.4.166:11434")

    agent = Agent(load_tools(), llm=llm)

    terminal = UserTerminalChannel(agent)
    terminal.start()

if __name__ == "__main__":
    main()
