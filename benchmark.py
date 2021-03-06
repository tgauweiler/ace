import logging
import coloredlogs
import getConfigs
import scheduleJob
import datetime
import argparse
import time

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)-2s %(filename)s:%(lineno)s - %(funcName)5s()] %(message)s")

logging.getLogger('getConfigs').setLevel(logging.INFO)
logging.getLogger('scheduleJob').setLevel(logging.INFO)

logger = logging.getLogger('runBenchmark')
coloredlogs.install(level='DEBUG')

# FIXME: The config object share data! So change one can change many!


class Benchmark(object):
    def __init__(self, file):
        self.file = file
        self.configurations = getConfigs.parseConfig(file)

    def run(self):
        for config in self.configurations:
            scheduleJob.schedule(config)

    def update(self):
        # Update all job information
        for config in self.configurations:
            scheduleJob.get_job_info(config)

    def check_jobs(self):
        # Check all job status codes for errors and maybe retry
        for job in self.configurations:
            if 'jobid' in job:
                if job['status']['job_state'] == 'DEADLINE':
                    if 'retry' in job['scheduler'] and job['scheduler']['retry'] and 'retry-count' in job['scheduler']:
                        count = int(job['scheduler']['retry-count'])
                        if count > 0:
                            job['scheduler']['retry-count'] = str(count-1)
                            if 'time' in job['scheduler'] and 'retry-time' in job['scheduler']:
                                # Add retry time to time and rerun job
                                (h, m, s) = job['scheduler']['time'].split(':')
                                d = datetime.timedelta(
                                    hours=int(h), minutes=int(m), seconds=int(s))

                                (h, m,
                                 s) = job['scheduler']['retry-time'].split(':')
                                d = d + \
                                    datetime.timedelta(
                                        hours=int(h), minutes=int(m), seconds=int(s))

                                job['scheduler']['time'] = str(d)
                                scheduleJob.schedule(job)

                elif job['status']['job_state'] == 'FAILED':
                    if 'retry' in job['scheduler'] and job['scheduler']['retry'] and 'retry-count' in job['scheduler']:
                        count = int(job['scheduler']['retry-count'])
                        if count > 0:
                            job['scheduler']['retry-count'] = str(count-1)
                            # Maybe create new config so that failed job stays as gui line?
                            scheduleJob.schedule(job)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run benchmark for config.yml")
    parser.add_argument('config_file', metavar='file',
                        type=str, help='Path to config file')

    args = parser.parse_args()
    bench = Benchmark(args.config_file)

    logger.info("Run benchmark? (ctrl-c to abort)")
    input("")
    for i, config in enumerate(bench.configurations):
        scheduleJob.schedule(config, str(i))
        print('.', end='', flush=True)
        time.sleep(0.5)
    print("")  # So that shell starts correctly after termination
