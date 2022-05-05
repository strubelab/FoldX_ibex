"""
Boilerplate code for a wrapper
"""

import tempfile
import pandas as pd
import configparser
from pathlib import Path
from executor.executor import Executor


class FoldX(Executor):
    """
    Class to execute the FoldX `BuildModel` command in a given PDB structure
    """

    def __init__(self, pdb:Path, mutations:list, chains:list, out_dir:Path=None,
        tempdir:Path=None, **kw):
        """
        Instantiate variables
        """

        self.pdb = pdb
        self.tempdir = tempdir or Path(tempfile.mkdtemp(
            prefix=self.__class__.__name__.lower() + '_'))
        self.out_dir = out_dir or self.tempdir

        self.mutations = mutations
        self.chains = chains
        assert len(mutations) == len(chains)

        self.mutant_file = self.out_dir / 'individual_list.txt'

        config = configparser.ConfigParser()
        config.read(Path(__file__).parent/'config.ini')
        self.BIN = config['user.lib.files']['BIN'] or config['DEFAULT']['BIN']
        self.BIN = Path(self.BIN)

        self.args = (
            f'./foldx_20221231 '
            f'--command=BuildModel '
            f'--pdb={self.pdb.name} '
            f'--pdb-dir={self.pdb.parent.resolve()} '
            f'--mutant-file={self.mutant_file.resolve()} '
            f'--output-dir={self.out_dir.resolve()}'
        ).split()

        # Call the parent __init__ method from the Executor class
        # with the rest of the `kw` parameters (see source executor.py file)
        super().__init__(self.args, tempdir=self.tempdir, out_dir=self.out_dir,
                cwd=self.BIN, **kw)


    def prepare(self):
        """
        Prepare the input for your program (e.g. create the input files)
        """
        ## Call parent method to create a temporary directory and
        ## the output directory, if any
        super().prepare()

        # Put the mutations in the required format:
        # [from_residue][chain][number][to_residue],...,...;
        formatted_mutations = []
        for i, c in enumerate(self.chains):
            imuts = self.mutations[i]
            formatted_mutations += [m[0]+c+m[1:] for m in imuts]

        # Write the mutations to the `individual_list.txt` file
        with open(self.mutant_file, 'w') as f:
            f.write(','.join(formatted_mutations) + ';')
    
            
    def finish(self):
        """
        Read the output differences in deltaG from the file Raw_{pdb}.fxout
        """
        pdbid = self.pdb.stem
        out_file = self.out_dir / f'Dif_{pdbid}.fxout'

        diff = pd.read_csv(out_file, sep='\t', header=7)
        diff = diff.T.drop(['Pdb']).astype('float64')

        # diff is now a dataframe with 1 column labeled 0, so just return it as
        # a series
        return diff[0]
