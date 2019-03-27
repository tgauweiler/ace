import yaml

"""
This file handles the configuration file loading and parsing
"""


def merge_dicts(main: dict, second: dict):
    """
    Merges two dicts into main

    Args:
        main (dict): The target dict
        second (dict): The dict to be added to main
    """

    for key, value in second.items():
        if key in main and type(value) is dict:
            merge_dicts(main[key], value)
        elif type(main) is dict and key not in main:
            main[key] = value


def load(filename: str) -> dict:
    """
    Loads a configuration file and parses

    Args:
        filename (str): Path to file

    Returns:
        dict: Parsed yaml
    """

    include_configs = dict()
    with open(filename, 'r') as f:
        for line in f:
            if '#include' in line:
                include_filename = line.split(' ')[1].strip()
                merge_dicts(include_configs, load(include_filename))
            else:
                break

    with open(filename, 'r') as stream:
        try:
            main_configs = yaml.load(stream)

        except yaml.YAMLError as exc:
            print(exc)
            raise

    # Merge main file with include file
    merge_dicts(main_configs, include_configs)

    return main_configs
