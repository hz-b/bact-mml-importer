from dataclasses import dataclass
from typing import Union, Sequence


@dataclass
class CurvePoint:
    indep: float
    dep: float


@dataclass
class CurveBasedConversionInfo:
    curve: Sequence[CurvePoint]


@dataclass
class ConversionInfo:
    offset: float
    meta_gain: float
    # Todo: instead of float use a LinearConversionInfo class
    #       or even better store only its identifier
    forward: Union[float, CurveBasedConversionInfo]
    backward: Union[float, CurveBasedConversionInfo]

@dataclass
class Magnet:
    type: str
    subtype: str
    name: str
    forward_curve: CurveBasedConversionInfo = None
    backward_curve: CurveBasedConversionInfo = None
    pc: str = ""