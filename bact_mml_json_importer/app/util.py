import pprint
from typing import Mapping, Sequence
import logging

logger = logging.getLogger("bact-mml-importer")


def make_single_entry_sequence_of_one(
    family_members: Mapping[str, Mapping], verbose: bool =False
):
    """handle families that consit only of one member"""
    if verbose:
        print("input --------- ")
        pprint.pprint(family_members)
        print("input ========")

    name = family_members["FamilyName"]
    if isinstance(family_members["ElementList"], Sequence):
        return family_members

    nf = family_members.copy()
    # first level
    for key in ["CommonNames", "ElementList", "Status", "DeviceList", "Position"]:
        nf[key] = [family_members.get(key, None)]
    # lattice info level
    if nf.get("AT", None) is not None:
        key = "ATIndex"
        val = family_members["AT"].get(key, None)
        if val is not None:
            nf["AT"][key] = [val]
        else:
            logger.warning(f"failed to retrieve {key} for {name}")
            # do a second try
            key = "ATParameterGroup"
            data_entry, = family_members["AT"].get(key)
            nf["AT"]["ATIndex"] = [datum["ElemIndex"] for datum in data_entry]


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

    if verbose:
        print("new ---------- ")
        pprint.pprint(nf)
        print("new ========= ")

    return nf
