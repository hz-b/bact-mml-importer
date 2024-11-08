from dataclasses import dataclass
from typing import Union


@dataclass
class ConversionInfo:
    offset: float
    meta_gain: float
    forward: float
    backward: float
