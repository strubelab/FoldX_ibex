import unittest
import os, sys, shutil
from  pathlib import Path
from Bio import SeqIO
import tempfile

import pandas as pd

sys.path.append(os.fspath(Path(__file__).parent.parent))

from example_wrapper.wrapper import Program


class ProgramTest(unittest.TestCase):

    def setUp(self):
        '''Called for every method'''
        self.seq_dir = Path(__file__).parent / 'test_outputs/'
        self.SeqRec = SeqIO.read(self.seq_dir/'seq.fasta', 'fasta')
        self.tempdir = Path(tempfile.gettempdir(),
            self.__class__.__name__.lower())
        self.dir_out = self.tempdir


        self.program = Program(self.SeqRec, dir_out=self.dir_out,
                                tempdir=self.tempdir, keep_tempdir=True)

    def test_command_created(self):
        """
        Test that the proper command is created in the __init__ method
        """
        self.assertEqual(self.program.args,
            (
            f'program_name '
            f'--param1 {self.param1} '
            f'--param2 {self.param2} '
            ).split())

    def test_creates_input_fasta(self):
        """
        Test that the prepare method creates the input fasta file
        """
        self.program.prepare()

        seq_file = self.dir_out / 'seq.fasta'

        self.assertTrue(seq_file.is_file())

        seq = SeqIO.read(seq_file, 'fasta')

        self.assertTrue(str(seq.seq), str(self.SeqRec.seq))

    def test_output_created(self):
        """
        Test that the output was created
        """
        # e.g. when the output is a pandas DataFrame
        output_df = self.program.run()
        test_pickle = Path(__file__).parent / 'test_outputs/output.pkl'
        expected_output = pd.read_pickle(test_pickle)
        self.assertTrue(expected_output.equals(output_df))

        # when the output is a file
        f_out = self.dir_out / 'output.out'
        self.assertTrue(f_out.is_file())


    def tearDown(self):
        '''If setUp() succeeded, tearDown() will be run whether the test method
        succeeded or not.'''
        
        if self.tempdir.exists():
            shutil.rmtree(self.tempdir)




if __name__ == '__main__':
    unittest.main()
