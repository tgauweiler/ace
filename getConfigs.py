import logging
import itertools
from loader import load

logger = logging.getLogger('getConfigs')


def resolve_python(element):
    if type(element) is dict:
        for k, v in element.items():
            if type(v) is dict:
                if 'eval' in v:
                    try:
                        logger.debug("Try eval: " + str(v['eval']))
                        element[k] = eval(v['eval'])
                        logger.debug("Evaled: " + str(element[k]))
                    except SyntaxError as e:
                        logger.warning("Eval error: " + str(e) + " line: " + element)
                else:
                    resolve_python(v)
            else:
                resolve_python(v)

    elif type(element) is list:
        for e in element:
            resolve_python(e)


def resolve_masks(element):
    if type(element) is dict:
        for k, v in element.items():
            if type(v) is dict and 'mask' in v and 'values' in v:
                mask = v['mask']
                numbers = v['values']
                count = mask.count('?')

                ret = list()
                if count > 1:
                    # Need to create all permutations to replace all ?
                    for x in itertools.product(numbers, repeat=count):
                        string = mask
                        for i in range(0, count):
                            string = string.replace('?', str(x[i]), 1)
                        ret.append(string)
                else:
                    for x in numbers:
                        string = mask.replace('?', str(x), 1)
                        ret.append(string)

                element[k] = ret
                logger.debug("Mask: " + mask + " val: " + str(numbers) + " permutations: " + str(ret))

            else:
                resolve_masks(v)

    elif type(element) == list:
        for e in element:
            resolve_masks(e)


def make_all_str(element):
    if type(element) == dict:
        for k, v in element.items():
            if type(v) is dict or type(v) is list:
                make_all_str(v)
            else:
                element[k] = str(v)

    elif type(element) is list:
        for i, e in enumerate(element):
            if type(e) is dict or type(e) is list:
                make_all_str(e)
            else:
                element[i] = str(e)


def make_list(element):
    if type(element) is dict:
        for k, v in element.items():
            if type(v) is str or type(v) is int or type(v) is float or type(v) is bool:
                element[k] = list()
                element[k].append(v)
            else:
                make_list(v)
    elif type(list) is list:
        for e in element:
            make_list(e)


def gen_combinations(d):
    keys, values = d.keys(), d.values()
    values_choices = (gen_combinations(v) if isinstance(v, dict) else v for v in values)
    for comb in itertools.product(*values_choices):
        yield dict(zip(keys, comb))


def parseConfig(filename: str) -> list:
    logger.info("Parsing config file: " + filename)

    config = load(filename)

    resolve_python(config)
    resolve_masks(config)

    make_list(config)  # Put everything into a list
    make_all_str(config)

    # Check for before_script and after_script (Join to string so that combination generation works)
    if 'before_script' in config:
        config['before_script'] = ["\n".join(config['before_script'])]
    if 'after_script' in config:
        config['after_script'] = ["\n".join(config['after_script'])]

    logger.info("Generating configurations..")
    job_configurations = list(gen_combinations(config))

    # Duplicate configs that have times set
    new = []
    for conf in job_configurations:
        if 'times' in conf['scheduler']:
            for x in range(1, int(conf['scheduler']['times'])):  # Conf exists already once
                new.append(conf)

    job_configurations.extend(new)

    logger.info("#Configurations: " + str(len(job_configurations)))

    if len(job_configurations) > 100:
        logger.warning("Large number of configurations generated!! " + str(len(job_configurations)))

    return job_configurations
