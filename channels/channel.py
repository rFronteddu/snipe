from abc import ABC, abstractmethod


class Channel(ABC):

    @abstractmethod
    def start(self):
        """
        Start listening for incoming messages.
        """
        pass

    @abstractmethod
    def send_message(self, recipient, message):
        """
        Send a message to a user through the channel.
        """
        pass
