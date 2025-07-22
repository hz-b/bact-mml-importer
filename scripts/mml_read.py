from bact_mml_json_importer.app.families import handle_families
from bact_mml_json_importer.app.inp import read_mml_in_json
from bact_mml_json_importer.app.machine import handle_machine_info
from bact_mml_json_importer.app.lattice import handle_at_lattice

import argparse
import sys


def families(filename: str):
    return handle_families(read_mml_in_json(filename=filename))


def machine_description(filename: str):
    return handle_machine_info(read_mml_in_json(filename=filename))

def at_lattice(filename: str):
    d = read_mml_in_json(filename=filename)
    r = handle_at_lattice(d['elements'])
    return r

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--families-file", help="json data of the object returned by getao()")
    parser.add_argument("--description-file", help="json data of the object returned by getad()")
    parser.add_argument("--at-lattice", help="at-lattice")
    out = parser.parse_args(sys.argv[1:])
    if out.description_file:
        des = machine_description(out.description_file)
        des

    if out.families_file:
        fam = families(out.families_file)
        fam

    if out.at_lattice:
        r = at_lattice(out.at_lattice)