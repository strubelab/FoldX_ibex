"""
Module to run a set of sequences through Program in an ibex job array
"""

import configparser
import pickle
from pathlib import Path

from executor.ibex import IbexRun


class FoldXIbex(IbexRun):
    """
    Class to run a set of sequences through raptorx in an ibex job array
    """

    def __init__(self, pdbs:list, mutations:list, chains:list, out_dir:Path,
        time_per_command:int=1, jobname:str='FoldXIbex', cpus:int=2,
        mem:int=4, **kw):
        """
        Defines the variables for the ibex job array to run Program.

        Args:
            pdbs (list):
                List of Paths with the PDBs to model mutations
            mutations (list):
                List of lists with the mutations for each pdb. The length needs
                to be the same as the pdb list
            chains (list):
                List of lists with the chains for each pdb. The length needs to
                be the same as the pdb list
            out_dir (Path):
                Directory to save the output for each protein sequence
            time_per_command (int, optional):
                Time to allocate for each run of FoldX in minutes.
            cpus (int, optional):
                Number of CPUs that each run of RaptorX will require.
                Defaults to 4.
            jobname (str, optional):
                Name of the job for ibex
        """
        self.pdbs = pdbs
        self.mutations = mutations
        self.chains = chains

        assert len(self.pdbs) == len(self.mutations) == len(self.chains)

        self.pdb_mut_chain = list(zip(self.pdbs, self.mutations, self.chains))
        
        # self.out_dir will contain the pickled DataFrames for each sequence
        self.out_dir = out_dir
        
        # self.out_ibex will contain the stdout for each ibex job
        self.out_ibex = self.out_dir / 'out_ibex'
        
        # self.pdbs_dir will contain the files with the pdbs and mutations to be
        # taken for each job
        self.pdbs_dir = self.out_dir / 'pdbs'
        
        self.jobname = jobname
        self.ncommands = len(self.pdbs)
        self.time_per_command = time_per_command
        self.cpus_per_task = cpus
        self.mem = mem

        self.python_file = Path(__file__).parent.resolve() / 'run_wrapper.py'

        config = configparser.ConfigParser()
        config.read(Path(__file__).parent/'config.ini')
        self.conda_env = Path(config['user.lib.files']['CONDA_ENV'])

        super().__init__(time_per_command=self.time_per_command,
            out_ibex=self.out_ibex, ncommands=self.ncommands,
            jobname=self.jobname, cpus_per_task=self.cpus_per_task,
            out_dir=self.out_dir, **kw)

    def write_pdbs(self):
        """
        Write the sequences in separate files, according to the number of
        commands to be run per job.
        """
        seq_ind=0
        
        for job_num in range(self.njobs):
            job_seqs = (
                self.pdb_mut_chain[ seq_ind : seq_ind + self.commands_per_job ])
            
            fname = self.pdbs_dir / f'pdbs{job_num}.pkl'
            with open(fname, 'wb') as f:
                pickle.dump(job_seqs, f)
            
            seq_ind += self.commands_per_job


    def prepare(self):
        """
        Generate the output directories and the script to be run. By default,
        the script file is saved in `{self.out_ibex}/script.sh`.
        """
        if not self.pdbs_dir.exists():
            self.pdbs_dir.mkdir(parents=True)
        if not self.out_ibex.exists():
            self.out_ibex.mkdir(parents=True)

        self.write_pdbs()

        self.script = (
            '#!/bin/bash --login\n'
            f'#SBATCH --job-name={self.jobname}\n'
            f'#SBATCH --partition={self.partition}\n'
            f'#SBATCH --output={self.out_ibex}/%J.out\n'
            f'#SBATCH --time={self.time_per_job}\n'
            f'#SBATCH --ntasks={self.ntasks}\n'
            f'#SBATCH --cpus-per-task={self.cpus_per_task}\n'
            f"#SBATCH --mem={self.mem}G\n"
            f'#SBATCH --array=0-{self.njobs-1}\n'
            '\n'
            f'conda activate {self.conda_env}\n'
            '\n'
            f'seq_file="{self.pdbs_dir.resolve()}/'
            'pdbs${SLURM_ARRAY_TASK_ID}.pkl"\n'
            f'python {self.python_file} '
            '${seq_file} '
            f'{self.out_dir}\n'
        )

        with open(self.script_file, 'w') as f:
            f.write(self.script)

