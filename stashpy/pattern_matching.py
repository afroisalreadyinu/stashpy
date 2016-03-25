import regex
import parse
import pkgutil

#parsing re's with re's. i'm going to hell for this.
NAMED_RE_RE = regex.compile(r"\(\?P<\w*>.*?\)")

def is_named_re(maybe_re):
    found = NAMED_RE_RE.findall(maybe_re)
    return found

class LineParser:

    def __init__(self, spec):
        if is_named_re(spec):
            self.re = regex.compile(spec)
            self.parse = None
        else:
            self.re = None
            self.parse = parse.compile(spec)

    def __call__(self, line):
        if self.re:
            match = self.re.match(line)
            if match is None:
                return None
            return match.groupdict()
        match = self.parse.parse(line)
        if match is None:
            return None
        return match.named

def read_patterns():
    data = pkgutil.get_data('stashpy', 'patterns/grok_patterns.txt').decode('utf-8')
    patterns = {}
    for line in data.split('\n'):
        if line.startswith('#') or line.strip() == '':
            continue
        name, expression = line.split(' ', maxsplit=1)
        patterns[name] = expression
    return patterns

GROK_PATTERNS = read_patterns()
GROK_REPLACE_PATTERN = regex.compile("\%\{(?P<pattern_name>\w*)(?P<pattern_output>:\w*)?\}")
GROK_NEW_PATTERN = "(?P<{name}>{pattern})"

def sub_pattern(match):
    match_dict = match.groupdict()
    pattern = GROK_PATTERNS[match_dict['pattern_name']]
    pattern_output_raw = match_dict['pattern_output']
    if pattern_output_raw:
        pattern_output = pattern_output_raw.lstrip(':')
        new_pattern = GROK_NEW_PATTERN.format(name=pattern_output, pattern=pattern)
    else:
        new_pattern = pattern
    return regex.sub(GROK_REPLACE_PATTERN, sub_pattern, new_pattern)

def compile(re_pattern):
    new_pattern = regex.sub(GROK_REPLACE_PATTERN, sub_pattern, re_pattern)
    return regex.compile(new_pattern)
