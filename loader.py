import yaml


# Result is saved in main
def merge_dicts(main: dict, second: dict):
    for key, value in second.items():
        if key in main and type(value) is dict:
            merge_dicts(main[key], value)
        elif type(main) is dict and key not in main:
            main[key] = value


def load(filename: str) -> dict:
    with open(filename) as f:
        first_line = f.readline()

        if '#include' in first_line:
            include_filename = first_line.split(' ')[1].strip()
            with open(include_filename, 'r') as stream:
                try:
                    include_configs = yaml.load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
                    raise

    with open(filename, 'r') as stream:
        try:
            main_configs = yaml.load(stream)

        except yaml.YAMLError as exc:
            print(exc)
            raise

    # Merge main file with include file
    if include_configs is not None:
        merge_dicts(main_configs, include_configs)
        # main_configs = {**include_configs, **main_configs}

    return main_configs
