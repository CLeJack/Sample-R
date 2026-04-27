from dataclasses import dataclass
from enum import Enum, auto
from collections import deque
from typing import Any

class MessageType(Enum):
    NULL = auto()
    # System/File Events
    IMPORT_FILES = auto()
    IMPORT_FOLDER = auto()
    IMPORT_FAILURE = auto()
    EXPORT_CYCLES = auto()
    EXPORT_WAVETABLE = auto()
    # UI State Events
    ELEMENT_SELECTED = auto()
    DATA_LOADED = auto()
    # Action Events
    REQ_REANALYZE = auto()
    UPDATE_INFO = auto()
    SORT = auto()
    ANALYZE = auto()
    TOP_MENU = auto()

@dataclass(frozen=True)
class UIMessage:
    msg_type: MessageType
    sender_id: int  # Changed to str for more descriptive IDs like "btn_import"
    value: Any

EMPTY_MSG = UIMessage(MessageType.NULL, "system", None)

class MessageBus:
    def __init__(self):
        self._queue = deque()

    def push(self, msg_type: MessageType, value: Any = "", sender_id: int = 0):
        msg = UIMessage(msg_type, sender_id, value)
        self._queue.append(msg)

    def pop(self) -> UIMessage:
        try:
            return self._queue.popleft()
        except IndexError:
            return EMPTY_MSG

bus = MessageBus()