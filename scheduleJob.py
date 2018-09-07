import logging
from slurmpy import Slurm
try:
    import pyslurm
except ImportError:
    logging.warning("Pyslurm not found, no job monitoring available!")

logger = logging.getLogger('scheduleJob')


def schedule(config: dict):
    if config['scheduler']['type'].lower() != 'slurm':
        logger.error("Only SLURM is supported at the moment!")
        raise RuntimeError("Unsupported Job Manager!")

    # Create Slurm job script
    parameters = {i: config['scheduler']['parameters'][i] for i in config['scheduler']['parameters'] if i != 'body'}

    job = Slurm("acb", parameters)

    body = ""
    if 'body' in config['scheduler']['parameters']:
        body += config['scheduler']['parameters']['body']

    call = config['exec']['call']

    for k, v in config['exec']['parameters'].items():
        if k in call:
            logger.debug(k + ' IS IN CALL!')
            if k + '=' in call:
                call = call.replace(k + '=', k + '=' + str(v))
            else:
                call = call.replace(k, k + ' ' + str(v))

    logger.debug(call)
    body += call

    config['jobid'] = 1 #job.run(body, _cmd="cat")

def get_job_info(jobid: str) -> list:
    if pyslurm:
        job = pyslurm.job()
        return job.find_id(jobid)
    else:
        return []
