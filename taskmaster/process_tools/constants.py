from enum import Enum


class StreamType(Enum):
    Stdout = 0
    Stderr = 1


class ProcessState(Enum):
    NotRunning = 1