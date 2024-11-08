import json
import logging

import jsons

from ..data_model.device.control_system_access import ControlSystemSignalType, ControlSystemSignal
from ..data_model.device.conversion_info import ConversionInfo
from ..data_model.device.device import InfoCommChannel, UnitNames, DeviceInfo
from ..data_model.family import FamilyMember, Family, Families, DeviceCountInfo
from ..data_model.lattice.lattice_element_info import LatticeInstance
from ..data_model.machine import MachineInfo, MachineMetaData, MachineType, DesignInfo, AdjustmentInfo
from ..data_model.survey_info import SurveyInformation

logger = logging.getLogger("bact-mml-read")






def load_mml_json_dumps():
    # can read it, but what for ...
    the_ring = read_mml_in_json("bessy2_the_ring_cfg.json")
    tmp = read_mml_in_json("bessy2_ad_cfg.json")
    machine_info = handle_machine_info(tmp)
    objs = jsons.dump(machine_info)
    with open("bessy2_ad_cfg_as_obj.json", "wt") as fp:
        json.dump(objs, fp, indent=4)

    tmp = read_mml_in_json("bessy2_ao_cfg.json")
    r = handle_families(tmp)
    objs = jsons.dump(r)
    with open("bessy2_ao_cfg_as_obj.json", "wt") as fp:
        json.dump(objs, fp, indent=4)

    bpm_x = r.get("BPMx")
    t = bpm_x.get("BPMZ5D1R")
    print(t)
    # see if caching works
    print(r.get("BPMx").get("BPMZ5D1R"))
    # see if caching works
    print(r.get("BPMx").get("BPMZ5D1R"))




def main():
    load_mml_json_dumps()
    with open("bessy2_ad_cfg_as_obj.json", "rt") as fp:
        txt = json.load(fp)

    minfo = jsons.load(txt, MachineInfo)
    minfo

    with open("bessy2_ao_cfg_as_obj.json", "rt") as fp:
        txt = json.load(fp)
    dev_lat_info = jsons.load(txt, Families)
    # dev_lat_info

