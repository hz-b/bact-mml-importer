from typing import Sequence, Union


def to_single_float_removing_zeros(values: Sequence[Union[float,int]]) -> float:
    r, =  [val for val in values if val != 0]
    return r


def clear_hw2physics(bpm_data, copy:bool=True):
    if copy:
        bpm_data = bpm_data.copy()
    t_vals = bpm_data["Monitor"]["HW2PhysicsParams"]
    vals = [
        to_single_float_removing_zeros(val) for val in t_vals
    ]
    bpm_data["Monitor"]["HW2PhysicsParams"] = vals
    return bpm_data
