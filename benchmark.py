import logging
import coloredlogs
import getConfigs
import scheduleJob
import datetime

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)-2s %(filename)s:%(lineno)s - %(funcName)5s()] %(message)s")

logging.getLogger('getConfigs').setLevel(logging.WARNING)
logging.getLogger('scheduleJob').setLevel(logging.WARNING)

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
                                d = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))

                                (h, m, s) = job['scheduler']['retry-time'].split(':')
                                d = d + datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))

                                job['scheduler']['time'] = str(d)
                                scheduleJob.schedule(job)

                elif job['status']['job_state'] == 'FAILED':
                    if 'retry' in job['scheduler'] and job['scheduler']['retry'] and 'retry-count' in job['scheduler']:
                        count = int(job['scheduler']['retry-count'])
                        if count > 0:
                            job['scheduler']['retry-count'] = str(count-1)
                            scheduleJob.schedule(job)  # Maybe create new config so that failed job stays as gui line?


if __name__ == "__main__":
    test = Benchmark('config_example.yml')
    print(str(type(test.configurations)))
    print(test.configurations[0])
    test.run()
    for job in test.configurations:
        # logger.debug(str(job))
        if 'widget' not in job and 'jobid' in job:
            print(job)

