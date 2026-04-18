from typing import List, Tuple

from deps_message_flow.messaging.common import IMessage
from deps_message_flow.messaging.producer import IMessageProducer

MessageInfo = Tuple[str, IMessage]


class FakeMessageProducer(IMessageProducer):
    def __init__(self, message_queue: List[MessageInfo]):
        self._message_queue = message_queue

    def send(self, destination: str, message: IMessage) -> None:
        self._message_queue.append((destination, message))
