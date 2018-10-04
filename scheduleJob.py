import logging
import os
import socket
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

    # If a host entry matches replace the found parameters
    if 'host' in config['scheduler']:
        hostname = socket.getfqdn()
        logger.debug("Hostname: " + hostname)
        if hostname in config['scheduler']['host']:
            logger.debug("Found host entry for this hostname")
            for k, v in config['scheduler']['host'][hostname]['parameters'].items():
                config['scheduler']['parameters'][k] = v

    # Create Slurm job script
    parameters = {i: config['scheduler']['parameters'][i] for i in config['scheduler']['parameters']}

    job = Slurm("acb", parameters)

    body = config['script']['body']

    env_vars = []
    auto_args = []
    for k, v in config['script']['parameters'].items():
        # Check if variable already set
        if k in os.environ:
            logger.warning(k + " environment variable already set!")

        # Set env variable
        if type(v) is dict:
            env_vars.append(k + "=\"" + v['values'] + "\"")
        else:
            env_vars.append(k + "=\"" + v + "\"")
            auto_args.append("--" + k + "=${" + k + "}")

    # Create auto_args
    if 'auto_args' in os.environ:
        logger.warning("auto_args environment variable already set!")
    env_vars.append("")  # Add a new line between args and auto_args
    env_vars.append("auto_args=\"" + " ".join(auto_args) + "\"")

    # Handle times keyword
    if 'times' in config['script'] and int(config['script']['times']) > 1:
        prefix = "for run in {1.." + config['script']['times'] + "}\ndo\n\n\n"
        suffix = "done"

    # Join body
    body = prefix + "\n".join(env_vars) + "\n\n\n" + body + "\n\n\n" + suffix + "\n"

    # Schedule job script
    config['jobid'] = job.run(body)


def get_job_info(config: dict):
    if pyslurm and 'jobid' in config:
        job = pyslurm.job()
        config['status'] = job.find_id(config['jobid'])[0]
