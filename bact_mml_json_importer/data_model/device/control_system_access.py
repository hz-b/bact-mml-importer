from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union


class ControlSystemSignalType(Enum):
    read_only = "ro"
    read_write = "rw"


@dataclass(frozen=True)
class ControlSystemSignal:
    # I prefer bluesky readback over monitor
    # its a bit more accurate
    sig_name: str
    type: ControlSystemSignalType
    conversion_function_name: Optional[str]
