# FoldX in ibex
---

# Installation

Skip these steps if you're using the version installed in ibex.

1. (Skip if you're using the version in ibex) Register at the [FoldX website](https://foldxsuite.crg.eu/academic-license-info), download and extract the program wherever you want to save it.

2. Clone this repository and go into the directory that was created

```bash
git clone https://github.com/strubelab/FoldX_ibex.git

cd FoldX_ibex
```

2. Create a virtual environment with the provided `environment.yml` file, and activate

```bash
conda env create --file environment.yml --prefix ./env
conda activate ./env
```

3. Install the `FoldX_ibex` package

```bash
pip install -e .
```

4. Download and install the Executor library (from a different directory)

```bash
# Go to your home directory, or wherever you want to install the Executor library
cd

# Clone the repository
git clone https://github.com/guzmanfj/Executor.git

# Install the library. Make sure the venv cretaed in step 2 is still activated
pip install -e ./Executor
```

# Usage

## Python class

You can run the wrapper from a python session or jupyter notebook. In this example we will model mutations on the `2oun` PDB structure. It has two identical chains, so we have to indicate them both in the `mutations` and `chains` arguments:

```python
from pathlib import Path
from FoldX.FoldX_ibex import FoldXIbex

# These have to be inside lists. You can give more than 1 pdb to model 
# many mutations in many PDBs
pdbs = [Path('./test/test_outputs/2oun.pdb')]
# One PDB, one mutation for chain A, and one for chain B
mutations = [[['L675W'], ['L675P']]]
# One PDB, chain A and chain B
chains = [['A','B']]

out_dir = Path('./output')

exe = FoldXIbex(pdbs, mutations, chains, out_dir=out_dir)
exe.run()
```

It will save in the `output_dir` a pickle file with the name of the pdb and the modeled mutations in the format `[from_aa][chain][number][to_aa]`. E.g. for the example the name will be `./output/2oun_LA675W_LB675P.pkl`.

## Command line program

You can also run the wrapper from the command line, but only for a single PDB file at a time:

```
$ foldx_wrapper --help
usage: foldx_wrapper [-h] --input INPUT [--mutations MUTATIONS [MUTATIONS ...]] [-d DESTINATION]

Takes a PDB file and one or more amino acid mutations

options:
  -h, --help            show this help message and exit
  --input INPUT         PDB file to model the mutation.
  --mutations MUTATIONS [MUTATIONS ...]
                        Mutations to model on the given PDB file, in the format [from_aa][chain][number][to_aa], e.g. LA675P
  -d DESTINATION, --destination DESTINATION
                        Path for saving the resulting energies in pickle format.
```
