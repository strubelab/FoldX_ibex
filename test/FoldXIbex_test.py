import unittest

import os, sys, shutil
import tempfile
from pathlib import Path

from Bio import SeqIO

sys.path.append(os.fspath(Path(__file__).parent.parent / 'example_wrapper'))

from wrapper_ibex import ProgramIbex

class ProgramIbexTest(unittest.TestCase):
    """
    Class for testing the Ibex module
    """

    def setUp(self) -> None:
        """
        Example case where there the test input is a fasta file with many
        sequences
        """
        self.sequences = list(SeqIO.parse(
            Path(__file__).parent / 'test_outputs' / 'sequences.fasta',
            'fasta'))
        self.tempdir = Path(tempfile.gettempdir(),
            self.__class__.__name__.lower())
        self.out_dir = self.tempdir
        self.out_ibex = self.out_dir / 'out_ibex'
        self.sequences_dir = self.out_dir / 'sequences'

        self.jobname = 'programibex_unittest'

        self.script_file = self.out_ibex / 'script.sh'
        
        self.programibex = ProgramIbex(self.sequences, out_dir=self.out_dir,
            tempdir=self.tempdir, jobname=self.jobname)
    

    def test_sequences_written(self) -> None:
        """
        Test that the sequence files were creating according to the number of
        sequences per job
        """
        
        file_names = [self.sequences_dir / f'sequences{i}.fasta' \
                        for i in range(10)]
        self.programibex.prepare()

        for i, file in enumerate(file_names):
            self.assertTrue(file.exists())
            seq = SeqIO.read(file, 'fasta')
            self.assertEqual(str(self.sequences[i].seq), str(seq.seq))

    def test_script_made(self) -> None:
        """
        Test that the script for ibex is made correctly
        """
        self.programibex.prepare()

        self.python_file = (Path(__file__).parent.parent.resolve()
                                / 'example_wrapper'
                                / 'run_wrapper.py')

        self.script = (
            '#!/bin/bash\n'
            f'#SBATCH --job-name=programibex_unittest\n'
            f'#SBATCH --partition=batch\n'
            f'#SBATCH --output={self.out_ibex}/%J.out\n'
            f'#SBATCH --time=00:17:00\n'
            f'#SBATCH --ntasks=1\n'
            f'#SBATCH --cpus-per-task=4\n'
            f"#SBATCH --mem-per-cpu=2G\n"
            f'#SBATCH --array=0-9\n'
            '\n'
            f'module load tgt_package'
            '\n'
            f'seq_file="{self.sequences_dir.resolve()}/'
            'sequences${SLURM_ARRAY_TASK_ID}.fasta"\n'
            f'python {self.python_file} '
            '${seq_file} '
            f'{self.out_dir}\n'
        )

        self.assertEqual(self.script, self.programibex.script)
        
        self.assertTrue(self.script_file.exists())
        with open(self.script_file, 'r') as f:
            script = f.read()
        self.assertEqual(self.script, script)

    def tearDown(self):
        '''If setUp() succeeded, tearDown() will be run whether the test method
        succeeded or not.'''
        if os.path.isdir(self.tempdir):
            shutil.rmtree(self.tempdir)

