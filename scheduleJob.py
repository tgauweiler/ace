import logging
from slurmpy import Slurm

logger = logging.getLogger('scheduleJob')

def schedule(config : dict):
    if config['scheduler']['type'].lower() != 'slurm':
        logger.error("Only SLURM is supported at the moment!")
        raise RuntimeError("Unsupported Job Manager!")

    # Create Slurm job script
    job = Slurm("", config['scheduler'])
    job.run("ls", _cmd="cat")

    #TODO: Move job monitor retry options out of config['scheduler']
    #TODO: Add config['scheduler']['body'] to slurm script body
    #TODO: Set a good jobname and save that name with jobID into config for monitoring