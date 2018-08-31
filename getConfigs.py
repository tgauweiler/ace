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


# https://stackoverflow.com/questions/50606454/cartesian-product-of-nested-dictionaries-of-lists
def gen_combinations(d):
    keys, values = d.keys(), d.values()
    combinations = itertools.product(*values)

    for c in combinations:
        yield dict(zip(keys, c))


def gen_dict_combinations(d):
    keys, values = d.keys(), d.values()
    for c in itertools.product(*(gen_combinations(v) for v in values)):
        yield dict(zip(keys, c))


# https://stackoverflow.com/questions/5228158/cartesian-product-of-a-dictionary-of-lists
# def product_dict(**kwargs):
#     keys = kwargs.keys()
#     vals = kwargs.values()
#     for instance in itertools.product(*vals):
#         yield dict(zip(keys, instance))
# print(list(product_dict(**config))[0])


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
    config['parameters'] = dict(pair for d in config['parameters'] for pair in d.items())
    config['scheduler'] = dict(pair for d in config['scheduler'] for pair in d.items())

    make_list(config)

    # Needed because gen_dict_combinations expects nested dict
    config['exec'] = {'call': config['exec']}

    logger.info("Generating configurations..")

    job_configurations = list(gen_dict_combinations(config))

    logger.info("#Configurations: " + str(len(job_configurations)))

    return job_configurations











