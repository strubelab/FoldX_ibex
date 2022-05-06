import unittest

import os, shutil
import tempfile
from pathlib import Path
import pickle
from FoldX.FoldX_ibex import FoldXIbex

class FoldXIbexTest(unittest.TestCase):
    """
    Class for testing the Ibex module
    """

    def setUp(self) -> None:
        """
        Example case where there the test input is a fasta file with many
        sequences
        """
        self.pdbs = [Path('./test/test_outputs/2oun.pdb')] * 2
        self.mutations = [[['L675W'], ['L675P']]] * 2
        self.chains = [['A','B'],['A','B']]

        self.tempdir = Path(tempfile.gettempdir(),
            self.__class__.__name__.lower())
        self.out_dir = self.tempdir
        self.out_ibex = self.out_dir / 'out_ibex'
        self.pdbs_dir = self.out_dir / 'pdbs'

        self.jobname = 'foldxibex_unittest'

        self.script_file = self.out_ibex / 'script.sh'
        
        self.exe = FoldXIbex(self.pdbs, self.mutations, self.chains,
            out_dir=self.out_dir, tempdir=self.tempdir, jobname=self.jobname)
    

    def test_pdbs_mutations_written(self) -> None:
        """
        Test that the pickle files were created according to the number of
        sequences per job
        """
        file_names = [self.pdbs_dir / f'pdbs{i}.pkl' \
                        for i in range(2)]
        self.exe.prepare()

        for i, file in enumerate(file_names):
            self.assertTrue(file.exists())
            with open(file, 'rb') as f:
                pdb_muts = pickle.load(f)

        pdbs, mutations, chains = list(zip(pdb_muts))

        self.assertEqual(self.pdbs, pdbs)
        self.assertEqual(self.mutations, mutations)
        self.assertEqual(self.chains, chains)


    def test_script_made(self) -> None:
        """
        Test that the script for ibex is made correctly
        """
        self.exe.prepare()

        self.python_file = (Path(__file__).parent.parent.resolve()
                                / 'FoldX'
                                / 'run_wrapper.py')

        self.script = (
            '#!/bin/bash --login\n'
            f'#SBATCH --job-name=foldxibex_unittest\n'
            f'#SBATCH --partition=batch\n'
            f'#SBATCH --output={self.out_ibex}/%J.out\n'
            f'#SBATCH --time=00:01:00\n'
            f'#SBATCH --ntasks=1\n'
            f'#SBATCH --cpus-per-task=2\n'
            f"#SBATCH --mem=4G\n"
            f'#SBATCH --array=0-1\n'
            '\n'
            f'conda activate {self.exe.conda_env}'
            '\n'
            f'seq_file="{self.pdbs_dir.resolve()}/'
            'pdbs${SLURM_ARRAY_TASK_ID}.pkl"\n'
            f'python {self.python_file} '
            '${seq_file} '
            f'{self.out_dir}\n'
        )

        self.assertEqual(self.script, self.exe.script)
        
        self.assertTrue(self.script_file.exists())
        with open(self.script_file, 'r') as f:
            script = f.read()
        self.assertEqual(self.script, script)

    def tearDown(self):
        '''If setUp() succeeded, tearDown() will be run whether the test method
        succeeded or not.'''
        if os.path.isdir(self.tempdir):
            shutil.rmtree(self.tempdir)

if __name__ == '__main__':
    unittest.main()
