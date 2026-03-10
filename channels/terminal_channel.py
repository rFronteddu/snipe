from channels.channel import Channel
from core.message import Message

class UserTerminalChannel(Channel):
    """
    Simple terminal-based channel to interact with the agent locally.
    """

    def __init__(self, agent):
        self.agent = agent

    def start(self):
        print("=== User Terminal Channel Started ===")
        print("Type 'exit' to quit.\n")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Exiting...")
                break

            msg = Message(sender="user_terminal", content=user_input, channel="terminal")
            response = self.agent.handle_message(msg)
            self.send_message(msg.sender, response)

    def send_message(self, recipient, message):
        print(f"Agent: {message}")
