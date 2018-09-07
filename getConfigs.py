import logging
import yaml
import itertools

logger = logging.getLogger('getConfigs')


def resolve_python(element):
    if type(element) == dict:
        for k, v in element.items():
            if type(v) == list:
                if len(v) == 1 and type(v[0]) == dict and 'python' in v[0]:
                    try:
                        logger.debug("Try eval: " + str(v[0]['python']))
                        element[k] = eval(v[0]['python'])
                        logger.debug("Evaled: " + str(element[k]))
                    except SyntaxError as e:
                        logger.warning("Eval error: " + str(e) + " line: " + element)
                else:
                    resolve_python(v)
            else:
                resolve_python(v)

    elif type(element) == list:
        for e in element:
            resolve_python(e)


def resolve_ranges(element):
    if type(element) == dict:
        for k, v in element.items():
            if type(v) == list:
                if len(v) == 2:
                    if type(v[0]) == int and type(v[1]) == int:
                        # Do range
                        v = range(v[0], v[1]+1)
                        element[k] = list(v)
                        logger.debug(k + " : " + str(element[k]))
                    else:
                        # Could be a list with two dicts
                        resolve_ranges(v)
                else:
                    # Bigger list continue
                    resolve_ranges(v)

    elif type(element) == list:
        for e in element:
            resolve_ranges(e)


def resolve_masks(element):
    if type(element) == dict:
        for k, v in element.items():
            if type(v) == list:
                if len(v) == 2 and type(v[0]) == dict and type(v[1]) == dict and 'mask' in v[0] and 'val' in v[1]:
                    mask = v[0]['mask']
                    numbers = v[1]['val']
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


def resolve_sequences(element):
    if type(element) == dict:
        for k, v in element.items():
            if type(v) is dict:
                if all(value is None for value in v.values()):
                    element[k] = list(v.keys())
                else:
                    resolve_sequences(v)
            else:
                resolve_sequences(v)

    elif type(element) == list:
        for e in element:
            resolve_sequences(e)


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
    with open(filename, 'r') as stream:
        try:
            config = yaml.load(stream)

        except yaml.YAMLError as exc:
            print(exc)
            raise

    resolve_ranges(config)  # Always has to come first
    resolve_python(config)
    resolve_masks(config)
    resolve_sequences(config)

    # Join all dict into one
    config['exec'] = dict(pair for d in config['exec'] for pair in d.items())
    config['exec']['parameters'] = dict(pair for d in config['exec']['parameters'] for pair in d.items())
    config['scheduler'] = dict(pair for d in config['scheduler'] for pair in d.items())
    config['scheduler']['parameters'] = dict(pair for d in config['scheduler']['parameters'] for pair in d.items())

    make_list(config)
    make_all_str(config)

    logger.info("Generating configurations..")

    job_configurations = list(gen_combinations(config))


    logger.info("#Configurations: " + str(len(job_configurations)))

    if len(job_configurations) > 100:
        logger.warning("Large number of configurations generated!!")

    return job_configurations
