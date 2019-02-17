# -*- coding: utf-8 -*-

from urllib.parse import urlparse
import inspect
import string
import textwrap
import fabulous.color as color
from inspect import Signature


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


def tabulate(tabular_data, first_row_header=False, indent_level=0, **kwargs):
    buffer = ''
    if tabular_data:
        max_key_length = len(max([str(d[0]) for d in tabular_data], key=len))
        max_value_length = len(max([str(d[1]) for d in tabular_data], key=len))
        div = 2
        buffer += '-'*max_key_length + ' '*div + '-'*max_value_length + '\n'
        first = True
        for data in tabular_data:
            buffer += ' '*indent_level + str(data[0]).ljust(max_key_length+div) + str(data[1]).ljust(max_value_length) + '\n'
            if first_row_header and first:
                buffer += ' '*indent_level + '-'*max_key_length + ' '*div + '-'*max_value_length + '\n'
                first = False
        buffer += ' '*indent_level + '-'*max_key_length + ' '*div + '-'*max_value_length + '\n'
    return buffer


def has_method(obj, method_name, signature=None):
    for member in inspect.getmembers(obj, predicate=inspect.ismethod):
        member_method_name = member[0]
        member_method = member[1]
        if member_method_name == method_name:
            if signature is not None:
                return Signature.from_callable(member_method) == signature
            return True
    return False


def merge_dict_lists(first, second, dedupe=True):
    merged = {}
    merged.update(first)

    for k, v in second.items():
        if k not in merged:
            merged[k] = v
        else:
            if isinstance(v, list) and isinstance(merged[k], list):
                merged[k] += v
                if dedupe:
                    merged[k] = list(set(merged[k]))
            else:
                merged[k] = v
    return merged


class CliFormatter(string.Formatter):

    STYLES = {
        'bold': lambda text: color.bold(text),
        'h1': lambda text: color.h1(text),
        'italic': lambda text: color.italic(text),
        'section': lambda text: color.section(text),
        'strike': lambda text: color.strike(text),
        'underline': lambda text: color.underline(text),
        'black': lambda text: color.black(text),
        'blue': lambda text: color.blue(text),
        'cyan': lambda text: color.cyan(text),
        'green': lambda text: color.green(text),
        'magenta': lambda text: color.magenta(text),
        'red': lambda text: color.red(text),
        'white': lambda text: color.white(text),
        'yellow': lambda text: color.yellow(text),
        'black_bg': lambda text: color.black_bg(text),
        'blue_bg': lambda text: color.blue_bg(text),
        'cyan_bg': lambda text: color.cyan_bg(text),
        'green_bg': lambda text: color.green_bg(text),
        'magenta_bg': lambda text: color.magenta_bg(text),
        'red_bg': lambda text: color.red_bg(text),
        'white_bg': lambda text: color.white_bg(text),
        'yellow_bg': lambda text: color.yellow_bg(text),
        'highlight_black': lambda text: color.highlight_black(text),
        'highlight_blue': lambda text: color.highlight_blue(text),
        'highlight_cyan': lambda text: color.highlight_cyan(text),
        'highlight_green': lambda text: color.highlight_green(text),
        'highlight_magenta': lambda text: color.highlight_magenta(text),
        'highlight_red': lambda text: color.highlight_red(text),
        'highlight_white': lambda text: color.highlight_white(text),
        'highlight_yellow': lambda text: color.highlight_yellow(text)
    }

    def __init__(self):
        super(CliFormatter, self).__init__()
        self.indent_level = 0
        self.dedent = True

    def format(self, *args, **kwargs):
        if 'dedent' in kwargs:
            self.dedent = kwargs['dedent']
            del kwargs['dedent']
        formatted = super(CliFormatter, self).format(*args, **kwargs)
        #print(formatted)
        if self.dedent:
            return textwrap.dedent(formatted).strip('\n')
        else:
            return formatted

    def vformat(self, format_string, args, kwargs):
        self.indent_level = len(format_string) - len(format_string.lstrip()) - 1
        return super(CliFormatter, self).vformat(format_string, args, kwargs)

    def parse(self, format_string):
        temp = super(CliFormatter, self).parse(format_string)
        return temp;

    def format_field(self, value, format_spec):
        if format_spec == 'table':
            return tabulate(value, first_row_header=True, indent_level=self.indent_level)
        elif format_spec == 'table_no_header':
            return tabulate(value, first_row_header=False, indent_level=self.indent_level)
        elif format_spec in CliFormatter.STYLES:
            stylized = CliFormatter.STYLES[format_spec](value)
            #return super(CliFormatter, self).format_field(stylized, format_spec)
            return str(stylized)
        else:
            return super(CliFormatter, self).format_field(value, format_spec)
