from enum import Enum


class MessagingModeEnum(str, Enum):
    broker = "broker"
    transactional_outbox = "transactional_outbox"
