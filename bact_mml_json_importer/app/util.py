import pprint
from typing import Mapping, Sequence


def make_single_entry_sequence_of_one(
    family_members: Mapping[str, Mapping], verbose=False
):
    """handle families that consit only of one member"""
    if verbose:
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

    if verbose:
        print("new ---------- ")
        pprint.pprint(nf)
        print("new ========= ")

    return nf
