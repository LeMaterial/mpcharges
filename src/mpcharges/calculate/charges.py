import json
import os
import subprocess
import sys
from glob import glob
from shutil import copyfile

import pandas as pd
from monty.tempfile import ScratchDir
from pymatgen.command_line.bader_caller import BaderAnalysis
from pymatgen.io.vasp.outputs import Chgcar


def get_bader_data(
    filename: str,
    aeccar0_folder: str,
    aeccar2_folder: str,
    chgcar_folder: str,
    perl_chgcar_file: str,
    bader_path: str,
    result_path: str,
):
    """Function to run and parse Bader charge data from VASP file that have been
    formatted using the standard given in MP's AWS OpenData collection.
    The files are saved by their task_id's and are put into an MSONable JSON
    format based on Pymatgen's volumetric class.
    These files are loaded, saved back to their raw VASP formats.
    The AECCARs are added using existing Perl script and saved as
    CHGCAR_ref and then Bader executable is ran with Pymatgen's BaderAnalysis class.
    The output charges are then saved as json matching the original task_id.

    Args:
        filename (str): filename matching file in AECCARs and CHGCARs folders
        aeccar0_folder (str): path of AECCAR0 files
        aeccar2_folder (str): path of AECCAR2 files
        chgcar_folder (str): path of CHGCAR files
        perl_chgcar_file (str): path of perl chgsum script
        bader_path (str): path of bader executable
        result_path (str): path of where to save results
    """
    with ScratchDir(".") as sd:
        # copy over CHGCAR, AECCARs files
        copyfile(os.path.join(chgcar_folder, filename), os.path.join(sd, "CHGCAR.json"))
        copyfile(
            os.path.join(aeccar0_folder, filename), os.path.join(sd, "AECCAR0.json")
        )
        copyfile(
            os.path.join(aeccar2_folder, filename), os.path.join(sd, "AECCAR2.json")
        )

        # JSON to RAW:
        for cf in ["AECCAR0", "AECCAR2", "CHGCAR"]:
            d = json.load(open(os.path.join(sd, "{}.json".format(cf)), "r"))
            Chgcar.from_dict(d["data"]).write_file(os.path.join(sd, cf))

        # run Perl script to add files
        params = [
            os.path.join(sd, "AECCAR0"),
            os.path.join(sd, "AECCAR2"),
        ]
        perl_script = subprocess.Popen([perl_chgcar_file, *params], stdout=sys.stdout)
        perl_script.communicate()
        # this creates CHGCAR_sum file

        # run Bader analysis
        ba = BaderAnalysis(
            os.path.join(sd, "CHGCAR"),
            chgref_filename=os.path.join(sd, "CHGCAR_sum"),
            bader_path=bader_path,
        )
        with open(
            os.path.join(result_path, "{}_result.json".format(filename)), "w"
        ) as fp:
            json.dump(ba.summary, fp)


def process_results_folder(result_path):
    """
    Takes all files processed using get_bader_data and creates
      final CSV with all summary information per task_id.

    Args:
        result_path (str): path of folder with files
            that have been processed with get_bader_data
    """
    result_files = glob(os.path.join(result_path, "*.json"))

    data = {
        "task_id": [],
        "charge": [],
        "min_dist": [],
        "atomic_volume": [],
        "vacuum_charge": [],
        "vacuum_volume": [],
        "reference_used": [],
        "bader_version": [],
    }

    for file in result_files:
        d = json.load(open(file))
        for key, value in d.items():
            data[key].append(value)
        data["task_id"].append(os.path.basename(file).replace("_result.json", ""))

    pd.DataFrame(data).to_csv(os.path.join(result_path, "summary.csv"))
