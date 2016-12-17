import sys
import json
import logging
import copy

from .pattern_matching import LineParser

logger = logging.getLogger(__name__)

class FormatSpec:

    def __init__(self, parser, out_format):
        self.parser = parser
        self.out_format = out_format

    def __call__(self, line):
        """Parse the line """
        result = self.parser(line)
        if result is None:
            return None
        output = copy.deepcopy(self.out_format)
        self._format_dict(output, result)
        return output

    def _format_dict(self, out_dict, value_dict):
        for key,val in out_dict.items():
            if isinstance(key, dict):
                self._format_dict(val, value_dict)
            else:
                out_dict[key] = val.format(**value_dict)


class LineProcessor:

    def __init__(self, specs=None):
        to_dict_specs, to_format_specs = [], {}
        if specs:
            to_dict_specs = specs.get('to_dict', [])
            to_format_specs = specs.get('to_format', {})
        else:
            if hasattr(self, 'TO_DICT'):
                to_dict_specs = self.TO_DICT
            if hasattr(self, 'TO_FORMAT'):
                to_format_specs = self.TO_FORMAT
        self.dict_specs = [LineParser(spec) for spec in to_dict_specs]
        self.format_specs = [FormatSpec(LineParser(format_spec), output_spec)
                             for format_spec, output_spec in to_format_specs.items()]


    def do_dict_specs(self, line):
        for dict_spec in self.dict_specs:
            dicted = dict_spec(line)
            if dicted:
                return dicted
        return None

    def do_format_specs(self, line):
        for format_spec in self.format_specs:
            formatted = format_spec(line)
            if formatted:
                return formatted
        return None

    def for_line(self, line):
        dict_result = self.do_dict_specs(line)
        if dict_result:
            return dict_result
        format_result = self.do_format_specs(line)
        if format_result:
            return format_result
        return None
