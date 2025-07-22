from typing import Dict, Sequence
import lat2db


def handle_at_lattice_element(d: Dict):
    pass

def handle_at_lattice(seq: Sequence[Dict]):
    return [handle_at_lattice_element(elem) for elem in seq]
    seq
    r = None
    return r