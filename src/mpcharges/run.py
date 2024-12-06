import os
from glob import glob

from mpcharges.calculate.charges import get_bader_data, process_results_folder

# load all file names - files must be unzipped
# can be downloaded from
# CHGCARs: https://materialsproject-parsed.s3.amazonaws.com/index.html#chgcars/
# AECCAR0: https://materialsproject-parsed.s3.amazonaws.com/index.html#aeccar0s/
# AECCAR2: https://materialsproject-parsed.s3.amazonaws.com/index.html#aeccar0s/
# sample AWS command:
# aws s3 cp --no-sign-request s3://materialsproject-parsed/aeccar2s/
# must be unziped: gunzip *.gz in directory
CHGCAR_FOLDER = "/path/to/CHGCARs/"
AECCAR0_FOLDER = "/path/to/AECCARs0/"
AECCAR2_FOLDER = "/path/to/AECCAR2"

# perl file can be downloaded from
# http://theory.cm.utexas.edu/code/vtstscripts.tgz
# but only chgsum.pl is needed from archive
PERL_CHGCARSUM_FILE = "/path/to/chgsum.pl"  # /ext/chgsum.pl
# bader executable precompiled for Linux
# can be downloaded from:
# https://theory.cm.utexas.edu/henkelman/code/bader/download/bader_lnx_64.tar.gz
BADER_PATH = "/path/to/bader"  # bader executable /ext/bader_linux

# this will yield to a bunch of mp-XXXXXXX.json
# files for results
RESULT_PATH = "results/"

if __name__ == "main":
    chgcar_files = [
        os.path.basename(x) for x in glob(os.path.join(CHGCAR_FOLDER, "mp-*.json"))
    ]
    aeccar0_files = [
        os.path.basename(x) for x in glob(os.path.join(AECCAR0_FOLDER, "mp-*.json"))
    ]
    aeccar2_files = [
        os.path.basename(x) for x in glob(os.path.join(AECCAR2_FOLDER, "mp-*.json"))
    ]

    # find all MP_IDs that have all 3 files
    files = set(chgcar_files)
    files.intersection_update(aeccar0_files)
    files.intersection_update(aeccar2_files)

    for file in files:  # these are the tasks that can be parallelized
        # make temporary folder
        get_bader_data(
            file,
            AECCAR0_FOLDER,
            AECCAR2_FOLDER,
            CHGCAR_FOLDER,
            PERL_CHGCARSUM_FILE,
            BADER_PATH,
            RESULT_PATH,
        )
    process_results_folder(RESULT_PATH)
