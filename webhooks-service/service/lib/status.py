from num import Enum, auto


class ShotStatus(Enum):
    OMIT = auto()
    BID = auto()
    HOLD = auto()
    AWAITING_MEDIA = auto()
    ACTIVE = auto()
    FINAL = auto()


class TaskStatus(Enum):
    OMIT = auto()
    HOLD = auto()
    WAITING = auto()
    READY = auto()
    PULL_ERROR = auto()
    IN_PROGRESS = auto()
    NEEDS_CLARIFICATION = auto()

