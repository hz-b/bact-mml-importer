import json
import logging
import pprint
from enum import Enum
from itertools import zip_longest
from typing import Mapping, Sequence, Union

import jsons

from ..data_model.device.control_system_access import ControlSystemSignalType, ControlSystemSignal
from ..data_model.device.conversion_info import ConversionInfo
from ..data_model.device.device import InfoCommChannel, UnitNames, DeviceInfo
from ..data_model.family import FamilyMember, Family, Families, DeviceCountInfo
from ..data_model.lattice.lattice_element_info import LatticeInstance
from ..data_model.machine import MachineInfo, MachineMetaData, MachineType, DesignInfo, AdjustmentInfo
from ..data_model.survey_info import SurveyInformation

logger = logging.getLogger("bact-mml-read")


class ChannelType(Enum):
    readback = "readback"
    setpoint = "setpoint"



def make_single_entry_sequence_of_one(family_members: Mapping[str, Mapping]):
    """handle families that consit only of one member"""
    print("input --------- ")
    pprint.pprint(family_members)
    print("input ========")

    if isinstance(family_members["ElementList"], Sequence):
        return family_members

    nf = family_members.copy()
    # first level
    for key in ["CommonNames", "ElementList", "Status", "DeviceList", "Position"]:
        nf[key] = [family_members.get(key, None)]
    # lattice info level
    if nf.get("AT", None) is not None:
        for key in ["ATIndex"]:
            nf["AT"][key] = [family_members["AT"][key]]

    def conv_dict(ref):
        return {
            key: [ref[key]]
            for key in ["ChannelNames", "HW2PhysicsParams", "Physics2HWParams"]
        }

    for key in ["Monitor", "Setpoint"]:
        d = family_members.get(key)
        if d is not None:
            nd = d.copy()
            nd.update(conv_dict(d.copy()))
            nf[key] = nd

    print("new ---------- ")
    pprint.pprint(nf)
    print("new ========= ")
    return nf


def handle_conversion_info(
    conversion_info: Mapping[str, Union[None, str, Sequence[Union[str, float]]]],
    channel_type: ChannelType,
    n_elements: int,
):

    channels = conversion_info.get("ChannelNames")
    if not channels:
        channels = [None] * n_elements

    channel_type = ChannelType(channel_type)
    if channel_type == ChannelType.readback:
        converter = conversion_info.get("SpecialFunctionGet")
        sig_type = ControlSystemSignalType.read_only
    elif channel_type == ChannelType.setpoint:
        converter = conversion_info.get("SpecialFunctionSet")
        sig_type = ControlSystemSignalType.read_write
    else:
        raise AssertionError("Sanity check: should not end up here")

    # prepared for one signal here .. not 2
    offsets = conversion_info.get("Offset")
    if offsets is None:
        offsets = [None] * n_elements
    meta_gain = conversion_info.get("MetaGain")
    if meta_gain is None:
        meta_gain = [None] * n_elements

    # have to be vectors
    len(channels)
    len(offsets)
    len(meta_gain)

    hw2physics = conversion_info["HW2PhysicsParams"]
    try:
        len(hw2physics)
    except TypeError:
        hw2physics = [hw2physics]

    physics2hw = conversion_info["Physics2HWParams"]
    try:
        len(physics2hw)
    except TypeError:
        physics2hw = [physics2hw]

    conv_info_dm = [
        ConversionInfo(offset=offset, meta_gain=meta_gain, backward=hw2p, forward=p2hw)
        for offset, meta_gain, hw2p, p2hw in zip(
            offsets, meta_gain, hw2physics, physics2hw
        )
    ]

    comm_dm = [
        ControlSystemSignal(
            sig_name=sig_name, type=sig_type, conversion_function_name=converter
        )
        for sig_name in channels
    ]
    info_comms = [
        InfoCommChannel(info=info, comm=comm)
        for info, comm in zip(conv_info_dm, comm_dm)
    ]
    return info_comms


def handle_device_info(
    readback: Mapping[str, Union[str, Sequence[Union[str, float]]]],
    setpoint: Mapping[str, Union[str, Sequence[Union[str, float]]]],
    n_elements: int,
):

    conv_info_rdbk = handle_conversion_info(
        readback, ChannelType.readback, n_elements=n_elements
    )
    if setpoint:
        conv_info_setp = handle_conversion_info(
            setpoint, ChannelType.setpoint, n_elements=n_elements
        )
        limits = setpoint["Range"]
    else:
        conv_info_setp = [None] * len(conv_info_rdbk)
        limits = [None] * len(conv_info_rdbk)
    unit_names = UnitNames(
        hardware=readback["HWUnits"], physics=readback["PhysicsUnits"]
    )
    getter = readback.get("SpecialFunctionGet")

    r = [
        DeviceInfo(
            unit_names=unit_names,
            limits=lim,
            setpoint=setp,
            monitor=rdbk,
        )
        for setp, rdbk, lim in zip(conv_info_setp, conv_info_rdbk, limits)
    ]
    return r


def handle_family_members(family_members: Mapping[str, Mapping], t_type: str):
    family_members = make_single_entry_sequence_of_one(family_members)
    lattice_info = family_members.get("AT", None)
    if lattice_info is None:
        lattice_elems_info = [None]
    else:
        lattice_type = lattice_info["ATType"]
        at_indices = lattice_info["ATIndex"]

        lattice_elems_info = [
            LatticeInstance(index=lattice_index, type=lattice_type)
            for lattice_index in zip(at_indices)
        ]
    del lattice_info

    survey_pos = family_members.get("Position", None)
    if survey_pos is None:
        survey_device_info = [None]
    else:
        survey_device_info = [
            SurveyInformation(longitudinal_position=s) for s in survey_pos
        ]
    del survey_pos

    dev_cnt_info = [
        DeviceCountInfo(sector=sector, element_number=elem_num)
        for sector, elem_num in family_members["DeviceList"]
    ]

    dev_info = handle_device_info(
        family_members["Monitor"],
        family_members.get("Setpoint", None),
        len(dev_cnt_info),
    )

    wvf_idx = family_members.get("WaveRecordIndex", [None])
    if wvf_idx is None:
        pass
    common_names = family_members.get("CommonNames", None)
    if common_names is None:
        # Todo: can we let that pass on ?
        common_names = [None]
    else:
        common_names = [name.strip() for name in common_names]

    r = [
        FamilyMember(
            _name=name,
            type=t_type,
            status=status,
            survey=survey,
            dev_info=dev_info,
            lattice=lat_info,
            pos=pos,
        )
        for name, status, device_index, element_index, wave_record_index, survey, lat_info, pos, dev_info in zip_longest(
            common_names,
            family_members["Status"],
            family_members["DeviceList"],
            family_members["ElementList"],
            wvf_idx,
            survey_device_info,
            lattice_elems_info,
            dev_cnt_info,
            dev_info,
        )
    ]
    return r


def handle_families(families_json: Mapping[str, Union[str, Mapping]]) -> Families:
    def convert(families_info):
        t_type = families_info.get("FamilyType")
        return Family(
            name=families_info.get("FamilyName"),
            elements=handle_family_members(families_info, t_type),
        )

    return Families(
        elements=[convert(families_info) for _, families_info in families_json.items()]
    )


def handle_machine_info(
    machine_json: Mapping[str, Union[str, float, int, Mapping]]
) -> MachineInfo:

    return MachineInfo(
        standard_meta_data=MachineMetaData(
            machine=machine_json["Machine"],
            submachine=machine_json["SubMachine"],
            model=machine_json["ATModel"],
            mode=machine_json["ModeName"],
        ),
        machine_type=MachineType(machine_json["MachineType"]),
        design_info=DesignInfo(
            #: Todo: convert to eV?
            energy=machine_json["Energy"],
            length=machine_json["Circumference"],
            injection_energy=machine_json["InjectionEnergy"],
            harmonic_number=machine_json["HarmonicNumber"],
        ),
        adjustment_info=AdjustmentInfo(
            delta_radio_frequency_dispersion=machine_json["DeltaRFDisp"],
            mcf=machine_json["MCF"],
            tune_delay=machine_json["TuneDelay"],
        ),
    )


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


def read_mml_in_json(filename):
    with open(filename, "rt") as fp:
        txt = json.load(fp)
    return jsons.load(txt)


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

