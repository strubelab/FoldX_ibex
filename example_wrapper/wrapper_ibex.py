"""
Module to run a set of sequences through Program in an ibex job array
"""

import sys
import os
from Bio import SeqIO

from pathlib import Path

from executor.ibex import IbexRun


class ProgramIbex(IbexRun):
    """
    Class to run a set of sequences through raptorx in an ibex job array
    """

    def __init__(self, sequences:list, out_dir:Path, time_per_command:int=15,
        jobname:str='ProgramIbex', cpus:int=4, **kw):
        """
        Defines the variables for the ibex job array to run Program.

        Args:
            sequences (list):
                Lisf of SeqRecords to predict RaptorX properties
            out_dir (Path):
                Directory to save the output for each protein sequence
            time_per_command (int, optional):
                Time to allocate for each run of Program. Defaults to 15.
            cpus (int, optional):
                Number of CPUs that each run of RaptorX will require.
                Defaults to 4.
            jobname (str, optional):
                Name of the job for ibex
        """
        self.sequences = sequences
        
        # self.out_dir will contain the output file(s) for each sequence
        self.out_dir = out_dir
        
        # self.out_ibex will contain the stdout for each ibex job
        self.out_ibex = self.out_dir / 'out_ibex'
        
        # self.sequences_dir will contain the files with the sequences to be
        # taken for each job
        self.sequences_dir = self.out_dir / 'sequences'
        
        self.jobname = jobname
        self.ncommands = len(sequences)
        self.time_per_command = time_per_command
        self.cpus_per_task = cpus

        self.python_file = Path(__file__).parent.resolve() / 'run_wrapper.py'

        super().__init__(time_per_command=self.time_per_command,
            out_ibex=self.out_ibex, ncommands=self.ncommands,
            jobname=self.jobname, cpus_per_task=self.cpus_per_task, **kw)

    def write_sequences(self):
        """
        Write the sequences in separate files, according to the number of
        commands to be run per job.
        """
        seq_ind=0
        
        for job_num in range(self.njobs):
            job_seqs = (
                self.sequences[ seq_ind : seq_ind + self.commands_per_job ])
            
            SeqIO.write(
                job_seqs, self.sequences_dir / f'sequences{job_num}.fasta',
                'fasta')
            
            seq_ind += self.commands_per_job


    def prepare(self):
        """
        Generate the output directories and the script to be run. By default,
        the script file is saved in `{self.out_ibex}/script.sh`.
        """
        if not self.sequences_dir.exists():
            self.sequences_dir.mkdir(parents=True)
        if not self.out_ibex.exists():
            self.out_ibex.mkdir(parents=True)

        self.write_sequences()

        self.script = (
            '#!/bin/bash\n'
            f'#SBATCH --job-name={self.jobname}\n'
            f'#SBATCH --partition={self.partition}\n'
            f'#SBATCH --output={self.out_ibex}/%J.out\n'
            f'#SBATCH --time={self.time_per_job}\n'
            f'#SBATCH --ntasks={self.ntasks}\n'
            f'#SBATCH --cpus-per-task={self.cpus_per_task}\n'
            f"#SBATCH --mem-per-cpu={self.mem_per_cpu}G\n"
            f'#SBATCH --array=0-{self.njobs-1}\n'
            '\n'
            f'module load ibex_module'
            '\n'
            f'seq_file="{self.sequences_dir.resolve()}/'
            'sequences${SLURM_ARRAY_TASK_ID}.fasta"\n'
            f'python {self.python_file} '
            '${seq_file} '
            f'{self.out_dir}\n'
        )

        with open(self.script_file, 'w') as f:
            f.write(self.script)

