# MPCharges
Script used to calculate charges based on all available raw VASP files in Materials Project AWS OpenData initiatives.

### Requirements
- Python 3.10+
- Bader [download from here and unzip](https://theory.cm.utexas.edu/henkelman/code/bader/download/bader_lnx_64.tar.gz)
- VTST's scripts but only chgsum.pl [download from here and unzip](http://theory.cm.utexas.edu/code/vtstscripts.tgz)
- Pymatgen
- AWS CLI

### Raw files
- CHGCARs: `aws s3 cp --no-sign-request s3://materialsproject-parsed/chgcars/* .`
- AECCAR0s: `aws s3 cp --no-sign-request s3://materialsproject-parsed/aeccar0s/* .`
- AECCAR2s: `aws s3 cp --no-sign-request s3://materialsproject-parsed/aeccar2s/* .`

### Running the script
Download all CHGCAR into their own directory, keep the filename from the AWS bucket. 
Do the same for AECCAR0 into their own directory and the same for AECCAR2 into their own directory.

Change the directory variables (`CHGCAR_FOLDER`, `AECCAR0_FOLDER`, `AECCAR2_FOLDER`) in the `run.py`. 
Download the Bader executable and add the path (`BADER_PATH`) in `run.py`. Add the path (`PERL_CHGCARSUM_FILE`) of the `chgsum.pl` script from VTST scripts into the `run.py`.

Set a directory to congregate all the results (`RESULT_PATH`), a JSON file will be created for each calculation.

Run `run.py`.

### Behind the scenes.
The AECCAR0 and AECCAR2 are added and converted to CHGCAR_ref.
The Bader is run on the CHGCAR using the CHGCAR_ref as a reference via Pymatgen.
The result of charge and atomic volume is outputted to a json file.
