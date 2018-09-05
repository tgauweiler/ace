import logging
import getConfigs
import scheduleJob

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)-2s %(filename)s:%(lineno)s - %(funcName)5s()] %(message)s")

logging.getLogger('getConfigs').setLevel(logging.INFO)
logging.getLogger('scheduleJob').setLevel(logging.DEBUG)

logger = logging.getLogger('runBenchmark')


class Benchmark(object):
    def __init__(self, file):
        self.configurations = self.configurations = getConfigs.parseConfig('config_example.yml')

    def run(self):
        scheduleJob.schedule(self.configurations[0])



