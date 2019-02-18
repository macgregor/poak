# -*- coding: utf-8 -*-

from urllib.parse import urlparse
import inspect
import string
import textwrap
import re
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


def tabulate(tabular_data, first_row_header=False, indent_level=0):
    """
    Only supports 2 column tables currently.
    :param tabular_data:
    :param first_row_header:
    :param indent_level:
    :param kwargs:
    :return:
    """
    return str(Table(tabular_data, first_row_header, indent_level))


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


def non_ansi_str_length(text):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    scrubbed = ansi_escape.sub('', text)
    return len(scrubbed)


class Table(object):
    def __init__(self, tabular_data, first_row_header=False, indent_level=0, col_space=2):
        self.tabular_data = tabular_data
        self.first_row_header = first_row_header
        self.indent_level = indent_level
        self.col_space = col_space

        self.formatter = CliFormatter()
        self.max_col_lengths = []
        for col in self.tabular_data[0]:
            self.max_col_lengths.append(0)

    def __str__(self):
        processed_data = self._process_tabular_data()
        buff = ''
        first = True
        for row in processed_data:
            if first:
                buff += self._header(row) + '\n'
                first = False
            else:
                buff += self._row(row) + '\n'
        buff += self._div()
        return buff

    def _header(self, row):
        if self.first_row_header:
            return '{}\n{}\n{}'.format(self._div(indent=False), self._row(row), self._div())
        else:
            return self._div(indent=False)

    def _row(self, row, indent=True):
        buff = ' ' * self.indent_level if indent else ''
        for i in range(0, len(row)):
            col = str(row[i])
            right_pad = ' ' * (self.max_col_lengths[i] + self.col_space-non_ansi_str_length(col))
            buff += col + right_pad
        return buff

    def _div(self, indent=True):
        buff = ' ' * self.indent_level if indent else ''
        for max_col_len in self.max_col_lengths:
            buff += '-'*max_col_len + ' '*self.col_space
        return buff

    def _process_tabular_data(self):
        rows = []
        for row in self.tabular_data:
            row_data = []
            for i in range(0, len(row)):
                # process text through string formatter
                col = str(row[i])
                row_data.append(self.formatter.format(col, dedent=False))

                # calculate new max len for column, not counting ansi characters
                non_ansi_len = non_ansi_str_length(col)
                current_max = self.max_col_lengths[i]
                self.max_col_lengths[i] = non_ansi_len if non_ansi_len > current_max else current_max
            rows.append(row_data)
        return rows


class CliFormatter(string.Formatter):
    """
    Extends string.Formatter to provide some bells and whistles:
        Tabular Data - `{foo:table}`:
            tabular_data = [('foo-header', 'bar-header'), ('row1, col1', 'row1, col2)'] # and so on...
            formatter.format('Here is a table\n{totally_tabular:table}', totally_tabular=tabular_data)
        ANSI Style Markup - `{foo:bold}`:
            formatter.format('{good:256_bright_green}, {bad:256_bright_red}', good="Awesome!", bad="Oh no!")
        Format raw text without an explicit value:
            formatter.format('{Awesome!:256_bright_green}, {Oh no!:256_bright_red}') # normally would raise a KeyError
        Auto de-dent - dedent=True (default):
            multiline_string = '''
            Normally this would be printed with the leading/trailing \\n and spaces.
            You could call textwrap.dedent() on the resulting string but the formatter
            handles it for you.
            '''
            formatter.format('No indention:\n{}', multiline_string) # dedent=true by default
            formatter.format('Indention:\n{}', multiline_string, dedent=False)
    """

    STYLES = {
        'bold': lambda text: color.bold(text),
        'italic': lambda text: color.italic(text),
        'strike': lambda text: color.strike(text),
        'underline': lambda text: color.underline(text),
        '256_bright_green': lambda text: color.bold(color.fg256('#00FF00', text)),
        '256_green': lambda text: color.bold(color.fg256('#00FF00', text)),
        '256_light_green': lambda text: color.fg256('#99ff00', text),
        '256_bright_yellow': lambda text: color.bold(color.fg256('#ffdd00', text)),
        '256_yellow': lambda text: color.fg256('#ffdd00', text),
        '256_light_yellow': lambda text: color.fg256('#ffff00', text),
        '256_bright_red': lambda text: color.bold(color.fg256('#ff0000', text)),
        '256_red': lambda text: color.bold(color.fg256('#ff0000', text)),
        '256_light_red': lambda text: color.fg256('#ff5500', text),
    }

    def __init__(self):
        super(CliFormatter, self).__init__()
        self.indent_level = 0
        self.dedent = True

    def format(self, *args, **kwargs):
        """
        You can use 'dedent' to have the formatter de-indent the final string for you which
        is nice when you are using heredoc style strings that preserve white space in a multiline
        string.

        :param args:
        :param kwargs:
        :return:
        """
        if 'dedent' in kwargs:
            self.dedent = kwargs['dedent']
            del kwargs['dedent']
        formatted = super(CliFormatter, self).format(*args, **kwargs)
        if self.dedent:
            formatted = textwrap.dedent(formatted).strip('\n')
        self.dedent = True
        self.indent_level = 0
        return formatted

    def vformat(self, format_string, args, kwargs):
        """
        Need to keep track of the indent level incase we generate new rows of text,
        e.g. a Table, so the indention level of the generated row matches

        :param format_string:
        :param args:
        :param kwargs:
        :return:
        """
        if isinstance(format_string, str):
            self.indent_level = len(format_string) - len(format_string.lstrip()) - 1
        return super(CliFormatter, self).vformat(format_string, args, kwargs)

    def get_value(self, key, args, kwargs):
        """
        Normally a key without a matching value would raise an error, but I want to
        be able to stylize plain text without having to make a variable and stick it
        in a map, e.g. formatter.format('{This is a string:bold}') instead of
        formatter.format('{placehold:bold}', {'placeholder': 'This is a string'})

        :param key:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            return super(CliFormatter, self).get_value(key, args, kwargs)
        except (IndexError, KeyError) as e:
            return key

    def format_field(self, value, format_spec):
        if format_spec == 'table' or format_spec == 'table_no_header':
            header = format_spec == 'table'
            return tabulate(value, first_row_header=header, indent_level=self.indent_level)
        elif format_spec in CliFormatter.STYLES:
            stylized = CliFormatter.STYLES[format_spec](value)
            return str(stylized)
        else:
            return super(CliFormatter, self).format_field(value, format_spec)
