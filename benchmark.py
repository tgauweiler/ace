import logging
import coloredlogs
import getConfigs
import scheduleJob

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)-2s %(filename)s:%(lineno)s - %(funcName)5s()] %(message)s")

logging.getLogger('getConfigs').setLevel(logging.INFO)
logging.getLogger('scheduleJob').setLevel(logging.DEBUG)

logger = logging.getLogger('runBenchmark')
coloredlogs.install(level='DEBUG')


class Benchmark(object):
    def __init__(self, file):
        self.file = file
        self.configurations = getConfigs.parseConfig(file)

    def run(self):
        scheduleJob.schedule(self.configurations[0])


if __name__ == "__main__":
    test = Benchmark('config_example.yml')
    test.run()

