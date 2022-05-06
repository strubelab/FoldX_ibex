"""
Script that will be called for each job in ibex
To be used only along with the ibex wrapper
"""

from subprocess import CalledProcessError
import sys
from FoldX import FoldX
from pathlib import Path
import logging
import pickle

from executor.executor import RunError


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# Take the file with sequences and the output directory from the command-line inputs
seqs_file = Path(sys.argv[1])
out_dir = Path(sys.argv[2])

with open(seqs_file, 'rb') as f:
    pdbs_mutations = pickle.load(f)

# Run the Program wrapper for every sequence
for pdb, mutations, chains in pdbs_mutations:
    name = pdb.stem
    try:
        logging.info(f"Running FoldX for sequence {name}...")
        exe = FoldX(pdb, mutations, chains)
        output = exe.run()

        logging.info(f"Saving DataFrame to pickle...")
        output.to_pickle(out_dir / f'{name}.pkl')
    
    except (RunError, MemoryError, CalledProcessError) as e:
        logging.error(f"NO PROPERTIES CALCULATED FOR {name}")
        
