"""
Script that will be called for each job in ibex
To be used only along with the ibex wrapper
"""

from subprocess import CalledProcessError
import sys
from .wrapper import Program
from pathlib import Path
import logging

from Bio import SeqIO

from executor.executor import RunError


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# Take the file with sequences and the output directory from the command-line inputs
seqs_file = Path(sys.argv[1])
out_dir = Path(sys.argv[2])

sequences = list(SeqIO.parse(seqs_file, 'fasta'))

# Run the Program wrapper for every sequence
for seq in sequences:
    name = seq.name.split('|')[1]
    try:
        logging.info(f"Running Program for sequence {seq.name}...")
        exe = Program(seq)
        output = exe.run()

        logging.info(f"Saving DataFrame to pickle...")
        output.to_pickle(out_dir / f'{name}.pkl')
    
    except (RunError, MemoryError, CalledProcessError) as e:
        logging.error(f"NO PROPERTIES CALCULATED FOR {seq.name}")
        
