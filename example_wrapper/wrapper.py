"""
Boilerplate code for a wrapper
"""

import tempfile

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from pathlib import Path


from executor.executor import Executor


class Program(Executor):
    """
    Class to execute 'Program' on a given amino acid sequence, given
    as a SeqRecord
    """

    def __init__(self, sequence:SeqRecord, dir_out:Path=None,
        tempdir:Path=None, **kw):
        """
        Instantiate variables
        """

        self.SeqRec = sequence
        self.tempdir = tempdir or Path(tempfile.mkdtemp(
            prefix=self.__class__.__name__.lower() + '_'))
        self.dir_out = dir_out or self.tempdir

        # Define parameters for feeding into the program
        self.param1 = 'param1'
        self.param2 = 'param2'

        self.args = (
            f'program_name'
            f'--param1 {self.param1} '
            f'--param2 {self.param2} '
        ).split()

        # Call the parent __init__ method from the Executor class
        # with the rest of the `kw` parameters (see source executor.py file)
        super().__init__(self.args, tempdir=self.tempdir, **kw)

    
    def prepare(self):
        """
        Prepare the input for your program (e.g. create the input files)
        """
        ## Call parent method to create a temporary directory and
        ## the output directory, if any
        super().prepare()

        ## Write the fasta sequence to a file
        seq_file = self.dir_out / 'seq.fasta'

        if not seq_file.exists():
            SeqIO.write([self.SeqRec], seq_file, 'fasta')
    
            
    def finish(self):
        """
        Read output from your program, e.g. parse into a DataFrame or
        save to output file. Be sure to save the output in a location other
        than `self.tempdir`, which will be removed in the cleanup() method of
        the parent Executor class.
        """
        pass


    def isFailed(self):
        """
        Check that the output files were created successfully (optional)
        """
        fout = self.dir_out / 'output.txt'
        for file in self.files_out:
            if not file.exists():
                return f'{file} FILE WAS NOT CREATED'
            elif file.stat().st_size == 0:
                return f'{file} FILE IS EMPTY'
            
        return False