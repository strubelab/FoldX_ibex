import unittest
import socket
import shutil
from  pathlib import Path
import tempfile

import pandas as pd

from FoldX.FoldX import FoldX

class FoldXTest(unittest.TestCase):

    def setUp(self):
        '''Called for every method'''
        self.pdb_dir = Path(__file__).parent / 'test_outputs/'
        self.pdb = Path(self.pdb_dir/'2oun.pdb')
        self.mutations = [['L675W'], ['L675P']]
        self.chains = ['A', 'B']
        self.tempdir = Path(tempfile.gettempdir(),
            self.__class__.__name__.lower())
        self.out_dir = self.tempdir

        self.mutant_file = self.out_dir / 'individual_list.txt'

        self.exe = FoldX(self.pdb, self.mutations, self.chains,
            out_dir=self.out_dir, tempdir=self.tempdir, keep_tempdir=True)

    def test_command_created(self):
        """
        Test that the proper command is created in the __init__ method
        """
        self.assertEqual(self.exe.args,
            (
            f'./foldx_20221231 '
            f'--command=BuildModel '
            f'--pdb={self.pdb.name} '
            f'--pdb-dir={self.pdb_dir.resolve()} '
            f'--mutant-file={self.mutant_file.resolve()} '
            f'--output-dir={self.out_dir.resolve()}'
            ).split())

    def test_creates_mutant_list(self):
        """
        Test that the prepare method creates the input mutant list
        """
        self.exe.prepare()

        self.assertTrue(self.mutant_file.is_file())

        with open(self.mutant_file, 'r') as f:
            mutants = f.read()

        self.assertTrue(mutants, 'LA675W,LB675P;')

    def test_output_created(self):
        """
        Test that the output was created
        """
        host = socket.gethostname()
        if host.endswith('.local') or host.startswith('kl-'):
            self.skipTest("Needs to be run in ibex.")

        energy = self.exe.run()
        test_pickle = Path(__file__).parent / 'test_outputs/energy.pkl'
        expected_output = pd.read_pickle(test_pickle)
        self.assertTrue(expected_output.equals(energy))


    def tearDown(self):
        '''If setUp() succeeded, tearDown() will be run whether the test method
        succeeded or not.'''
        
        if self.tempdir.exists():
            shutil.rmtree(self.tempdir)




if __name__ == '__main__':
    unittest.main()
