from dataclasses import dataclass
from enum import Enum, auto
from collections import deque
from typing import Any

class ComponentType(Enum):
    NULL = auto()      # The "Empty" type
    BUTTON = auto()
    CHECKBOX = auto()
    TEXTENTRY = auto()
    SLIDER = auto()

@dataclass(frozen=True)
class UIMessage:
    sender_type: ComponentType
    sender_id: int
    value: Any


EMPTY_MSG = UIMessage(ComponentType.NULL, -1, '')

class MessageBus:
    def __init__(self):
        self._queue = deque()

    def push(self, msg: UIMessage):
        self._queue.append(msg)

    def pop(self) -> UIMessage:
        try:
            return self._queue.popleft()
        except IndexError:
            return EMPTY_MSG  # Return the Null Object instead of None

    def is_empty(self, msg: UIMessage) -> bool:
        return msg.sender_type == ComponentType.NULL

# Global instance
bus = MessageBus()