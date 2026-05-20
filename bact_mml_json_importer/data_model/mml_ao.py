import logging
from typing import Mapping, Union, Sequence, Tuple, Dict

from jsons import DeserializationError
from pydantic import BaseModel, ValidationError


logger = logging.getLogger("bact-mml-importer")


class ATElementsInfo(BaseModel):
    """To which
    """
    ATType: str
    ATIndex: int | Sequence[int] | Sequence[Sequence[int]]

# @dataclass
class ConversionFunctionHandle(BaseModel):
    file: str
    function: str
    type: str


# @dataclass
class ConversionFunction(BaseModel):
    function_handle: ConversionFunctionHandle


# @dataclass
class _MonitorBase(BaseModel):
    ChannelNames: Sequence[str] | str
    MemberOf: list[str] | None = None
    DataType: str
    Units: str
    HWUnits: str
    PhysicsUnits:str
    Mode: str | None  = None
    MetaGain:  Sequence[float] | None  = None
    PhysicalUnits: str | None  = None
    HW2PhysicsParams: Sequence[float] | float | None = None
    Physics2HWParams: Sequence[float] | float | None = None
    HW2PhysicsFcn: ConversionFunction | None = None
    Physics2HWFcn: ConversionFunction | None = None


#@dataclass
class MonitorDataModel(_MonitorBase):
    pass
    # model_config = ConfigDict(extra='allow')


# @dataclass
class SetpointDataModel(_MonitorBase):
    Range: Sequence[Tuple[float, float]] | Tuple[float, float]


# @dataclass
class FamilyInfoCollection(BaseModel):
    Status: Union[int, Sequence[int]]
    Position : Sequence[float] | None = None
    DeviceList : Sequence[Tuple[int,int]] | Tuple[int,int]
    ElementList : Sequence[int] | int
    MemberOf: Sequence[str] | str
    Monitor: MonitorDataModel | None = None
    Setpoint: SetpointDataModel | None = None
    CommonNames: Sequence[str] | str | None = None
    AT: ATElementsInfo | None = None

#    model_config = ConfigDict(extra='allow')


def load(data: Mapping[str, Union[str, Mapping]]) -> Dict[str, FamilyInfoCollection]:
    d = dict()
    for family_name, item in data.items():
        if family_name in ["TUNE", "DCCT"]:
            continue
        try:
            model = FamilyInfoCollection(**item)
            # model = jsons.load(item, FamilyInfoCollection)
        except DeserializationError as de:
            logger.error(f"Conversion failed for family {family_name}: de" )
            continue
        except ValidationError as ve:
            logger.error(f"Conversion failed for family {family_name}: {ve}" )
            continue
        d[family_name] = model
    return d
