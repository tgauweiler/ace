import logging
import pprint
import yaml
import itertools

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)-2s %(filename)s:%(lineno)s - %(funcName)5s()] %(message)s")


with open("config.yml", 'r') as stream:
    try:
        pp = pprint.PrettyPrinter(indent=4)
        config = yaml.load(stream)
        # pp.pprint(config)

    except yaml.YAMLError as exc:
        print(exc)
        raise


def resolve_python(element):
    if type(element) == dict:
        for k, v in element.items():
            if type(v) == list:
                if len(v) == 1 and type(v[0]) == dict and 'python' in v[0]:
                    try:
                        logging.info("Try eval: " + str(v[0]['python']))
                        element[k] = eval(v[0]['python'])
                        logging.info("Evaled: " + str(element[k]))
                    except SyntaxError as e:
                        logging.warning("Eval error: " + str(e) + " line: " + element)
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
                        logging.info(k + " : " + str(element[k]))
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
                    logging.info("Mask: " + mask + " val: " + str(numbers) + " permutations: " + str(ret))

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





resolve_ranges(config) # Always has to come first
resolve_python(config)
resolve_masks(config)
resolve_sequences(config)

pprint.pprint(config)








