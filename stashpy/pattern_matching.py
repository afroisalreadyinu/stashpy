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
        spec = grok_re_preprocess(spec)
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
GROK_REPLACE_PATTERN = regex.compile("\%\{(?P<pattern_name>\w*)(?P<pattern_output>:\w*)?(?P<pattern_type>:\w*)?\}")
GROK_NEW_PATTERN = "(?P<{name}>{pattern})"

class PatternTraverser:

    def __init__(self):
        self.pattern_types = {}

    def sub_pattern(self, match):
        match_dict = match.groupdict()
        pattern = GROK_PATTERNS[match_dict['pattern_name']]
        pattern_output_raw = match_dict['pattern_output']
        pattern_type_raw = match_dict['pattern_type']
        if pattern_output_raw:
            pattern_output = pattern_output_raw.lstrip(':')
            new_pattern = GROK_NEW_PATTERN.format(name=pattern_output, pattern=pattern)
            if pattern_type_raw:
                pattern_type = pattern_type_raw.lstrip(':')
                self.pattern_types[pattern_output] = __builtins__[pattern_type]
        else:
            new_pattern = pattern
        return regex.sub(GROK_REPLACE_PATTERN, self.sub_pattern, new_pattern)

def grok_re_preprocess(re_pattern):
    traverser = PatternTraverser()
    new_pattern = regex.sub(GROK_REPLACE_PATTERN, traverser.sub_pattern, re_pattern)
    return new_pattern, traverser.pattern_types
