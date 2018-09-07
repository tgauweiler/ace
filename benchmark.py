import logging
import coloredlogs
import getConfigs
import scheduleJob

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
        scheduleJob.schedule(self.configurations[0])


if __name__ == "__main__":
    test = Benchmark('config_example.yml')
    print(str(type(test.configurations)))
    print(test.configurations[0])
    test.run()
    for job in test.configurations:
        # logger.debug(str(job))
        if 'widget' not in job and 'jobid' in job:
            print(job)

