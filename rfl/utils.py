from copy import deepcopy

def merge_dict(default, *args):
    merged = deepcopy(default)

    for arg in args:
        for key, value in arg.items():
            if (key in merged) and isinstance(value, dict):
                merged[key] = merge_dict(merged[key], value)
            else:
                merged[key] = value

    return merged