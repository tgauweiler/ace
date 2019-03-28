import logging
import os
import socket
from slurmpy import Slurm

try:
    import pyslurm
except ImportError:
    logging.warning("Pyslurm not found, no job monitoring available!")

logger = logging.getLogger('scheduleJob')

"""
This file contains the logic to schedule and monitor one configuration as a job
"""


def schedule(config: dict, name_addition: str = None):
    """
    Schedules a given configuration as a new job

    Args:
        config (dict): job configuration
        name_addition (str, optional): Defaults to None. Addition to the job name

    Raises:
        RuntimeError: When requested scheduler is not available
    """

    executer = config['scheduler']['type'].lower()
    if executer not in ['slurm', 'bash']:
        logger.error("Only SLURM or bash are supported at the moment!")
        raise RuntimeError("Unsupported Job Manager!")

    # If a host entry matches replace the found parameters
    if 'host' in config['scheduler']:
        hostname = socket.getfqdn()
        logger.debug("Hostname: " + hostname)
        if hostname in config['scheduler']['host']:
            logger.debug("Found host entry for this hostname")
            for k, v in config['scheduler']['host'][hostname]['parameters'].items():
                config['scheduler']['parameters'][k] = v

    # Create Slurm job script, allow empty parameters
    try:
        parameters = {i: config['scheduler']['parameters'][i]
                      for i in config['scheduler']['parameters']}
    except KeyError:
        parameters = {}

    # Check if a log directory is set
    log_directory = None
    if 'log-directory' in config['script']:
        log_directory = config['script']['log-directory']

    # Check for job name
    job_name = "ace"
    if 'job-name' in config['scheduler']:
        job_name = config['scheduler']['job-name']

    job = Slurm(job_name, parameters, log_directory=log_directory)

    body = config['script']['body']

    env_vars = []
    auto_args = []

    # Add evn var with job id
    env_vars.append("jobId=" + name_addition)

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
    prefix = ''
    suffix = ''
    if 'times' in config['script']:
        prefix = "for run in {1.." + config['script']['times'] + "}\ndo\n\n\n"
        suffix = "done"

    # Handle before_script
    before_script = ''
    if 'before_script' in config:
        before_script = config['before_script']

    # Handle after_script
    after_script = ''
    if 'after_script' in config:
        after_script = config['after_script']

    # Join body
    body = before_script + "\n\n" + prefix + \
        "\n".join(env_vars) + "\n\n\n" + body + \
        "\n\n\n" + suffix + "\n\n" + after_script

    # Schedule job script
    if executer == 'bash':
        config['jobid'] = job.run(
            body, _cmd='bash', name_addition=name_addition)
    else:
        config['jobid'] = job.run(body, name_addition=name_addition)


def get_job_info(config: dict):
    """
    Gets runtime information of a running SLURM job

    Args:
        config (dict): A job configuration
    """

    if pyslurm and 'jobid' in config:
        job = pyslurm.job()
        config['status'] = job.find_id(config['jobid'])[0]
