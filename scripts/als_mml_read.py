import json
import os
import sys
from pathlib import Path

from bact_mml_json_importer.data_model.mml_ao import load


def main(filename):
    data = json.load(open(filename, "rt"))
    input_model = load(data["ao"])
    pass


if __name__ == "__main__":
    default_filename = Path(os.environ["HOME"]) / "Documents" / "dt4acc_als_data" / "MML_ao_BR_250410_raw.json"
    try:
        filename = Path(sys.argv[1])
    except IndexError:
        filename = default_filename
    main(filename)
