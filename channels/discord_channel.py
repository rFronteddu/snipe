# You type message in Discord
#        ↓
# Discord API triggers on_message
#        ↓
# DiscordChannel converts to Message
#        ↓
# Agent.handle_message()
#        ↓
# Agent runs tools or LLM
#        ↓
# Response returned
#        ↓
# Bot replies in Discord

import discord
from channels.channel import Channel
from core.message import Message


class DiscordChannel(Channel):

    def __init__(self, agent, token):
        self.agent = agent
        self.token = token

        intents = discord.Intents.default()
        intents.message_content = True

        self.client = discord.Client(intents=intents)

        @self.client.event
        async def on_message(discord_msg):

            if discord_msg.author == self.client.user:
                return

            message = Message(
                sender=str(discord_msg.author),
                content=discord_msg.content,
                channel="discord"
            )

            response = self.agent.handle_message(message)

            await discord_msg.channel.send(response)

    def start(self):
        self.client.run(self.token)

    def send_message(self, recipient, message):
        # For Discord we normally reply in the channel
        pass
