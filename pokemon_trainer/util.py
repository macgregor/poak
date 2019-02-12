# -*- coding: utf-8 -*-

from urllib.parse import urlparse


def extract_id_or_name(endpoint):
    parsed = urlparse(endpoint)
    if len(parsed.path) > 0:
        cleaned_path = parsed.path.lstrip('/').rstrip('/')
        last_segment = cleaned_path.split('/')[-1]
        try:
            return int(last_segment)
        except ValueError:
            return last_segment
    raise ValueError('No path segments in %s' % (endpoint))


def tabulate(tabular_data, **kwargs):
    buffer = ''
    if tabular_data:
        max_key_length = len(max([str(d[0]) for d in tabular_data], key=len))
        max_value_length = len(max([str(d[1]) for d in tabular_data], key=len))
        div = 2
        buffer += '-'*max_key_length + ' '*div + '-'*max_value_length + '\n'
        for data in tabular_data:
            buffer += str(data[0]).ljust(max_key_length+div) + str(data[1]).ljust(max_value_length) + '\n'
        buffer += '-'*max_key_length + ' '*div + '-'*max_value_length + '\n'
    return buffer


def merge_dict_lists(first, second, dedupe=True):
    merged = {}
    merged.update(first)

    for k, v in second.items():
        if k not in merged:
            merged[k] = v
        else:
            if isinstance(list, v) and isinstance(list, merged[k]):
                merged[k] += v
                if dedupe:
                    merged[k] = list(set(merged[k]))
            else:
                merged[k] = v
    return merged
