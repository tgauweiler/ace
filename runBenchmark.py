import logging
import getConfigs
import scheduleJob

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)-2s %(filename)s:%(lineno)s - %(funcName)5s()] %(message)s")

logging.getLogger('getConfigs').setLevel(logging.INFO)

logger = logging.getLogger('runBenchmark')

configurations = getConfigs.parseConfig('config_example.yml')

scheduleJob.schedule(configurations[0])
print(configurations[0])









