import json
import os
import sys
from pathlib import Path

from bact_mml_json_importer.data_model.mml_ao import load
from bact_mml_json_importer.util import clear_hw2physics


def main(filename):
    data = json.load(open(filename, "rt"))
    clear_hw2physics(data["BPMx"], copy=False)
    clear_hw2physics(data["BPMy"], copy=False)
    input_model = load(data)
    pass


if __name__ == "__main__":
    # / home / mfp / Devel / gitlab / mml - exported - data - sets / hz - b / bessyii / bessyii_ao_cfg.json
    default_filename = Path(os.environ["HOME"]) / "Devel" / "gitlab" / "mml-exported-data-sets" / "hz-b" / "bessyii" / "bessyii_ao_cfg.json"
    try:
        filename = Path(sys.argv[1])
    except IndexError:
        filename = default_filename
    main(filename)
