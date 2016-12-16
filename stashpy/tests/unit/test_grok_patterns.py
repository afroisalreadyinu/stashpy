import unittest
import regex
from stashpy import pattern_matching


class GrokPatternTests(unittest.TestCase):

    def test_normal_re(self):
        #A pattern without oniguruma patterns should work
        regexp = "My name is (?P<name>\w*) and I'm (?P<age>\d*) years old\."
        grokked_re, types = pattern_matching.grok_re_preprocess(regexp)
        self.assertDictEqual(types, {})
        compiled = regex.compile(grokked_re)
        self.assertDictEqual(
            compiled.match("My name is Takeshi and I'm 4 years old.").groupdict(),
            {"name": "Takeshi", "age": '4'})

    def test_simple(self):
        regexp = "My name is %{USERNAME:name} and I'm %{INT:age} years old"
        grokked_re, types = pattern_matching.grok_re_preprocess(regexp)
        self.assertDictEqual(types, {})
        compiled = regex.compile(grokked_re)
        self.assertDictEqual(
            compiled.match("My name is Takeshi and I'm 4 years old.").groupdict(),
            {"name": "Takeshi", "age": '4'})


    def test_skip_pattern(self):
        regexp = "My name is %{USERNAME:name} and I'm %{INT} years old"
        grokked_re, types = pattern_matching.grok_re_preprocess(regexp)
        self.assertDictEqual(types, {})
        compiled = regex.compile(grokked_re)
        self.assertDictEqual(
            compiled.match("My name is Takeshi and I'm 4 years old.").groupdict(),
            {"name": "Takeshi"})

    def test_pattern_synonym(self):
        regexp = "My name is %{USER:username} and I'm %{INT} years old"
        grokked_re, types = pattern_matching.grok_re_preprocess(regexp)
        self.assertDictEqual(types, {})
        compiled = regex.compile(grokked_re)
        self.assertDictEqual(
            compiled.match("My name is Takeshi and I'm 4 years old.").groupdict(),
            {"username": "Takeshi"})

    def test_pattern_types(self):
        regexp = "My name is %{USER:username} and I'm %{INT:age:int} years old"
        grokked_re, types = pattern_matching.grok_re_preprocess(regexp)
        self.assertDictEqual(types, {'age': int})
        compiled = regex.compile(grokked_re)
        self.assertDictEqual(
            compiled.match("My name is Takeshi and I'm 4 years old.").groupdict(),
            {"username": "Takeshi", "age": '4'})

    def test_embedded_patterns(self):
        regexp = "%{SYSLOGTIMESTAMP:timestamp}"
        grokked_re, types = pattern_matching.grok_re_preprocess(regexp)
        self.assertDictEqual(types, {})
        compiled = regex.compile(grokked_re)
        self.assertDictEqual(
            compiled.match("Mar 23 12:30:20").groupdict(),
            {"timestamp": "Mar 23 12:30:20"})
        self.assertDictEqual(
            compiled.match("Mar   23 12:30:20").groupdict(),
            {"timestamp": "Mar   23 12:30:20"})


    def test_nginx_log(self):
        regexp = '<%{INT}>%{SYSLOGTIMESTAMP:syslog_timestamp} %{SYSLOGHOST:host} %{IPORHOST:remote_addr} - %{USERNAME:remote_user}?- \[%{HTTPDATE:time_local}\] \"(?P<method>(GET|PUT|PATCH|POST|DELETE|HEAD|OPTIONS)) %{URIPATH:path}%{URIPARAM:params} HTTP/%{NUMBER:httpversion}\" %{INT:status} %{INT:body_bytes_sent}\"-\" %{QS:http_user_agent}'
        other_log = '<13>Mar 25 12:26:57 myserver.io 62.73.84.230 - - [25/Mar/2016:12:26:57 +0000] "GET /orders?order_identifier=AB075081&consumer_name=&consumer_first_name= HTTP/1.1" 200 1499"-" "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36"'
        grokked_re, types = pattern_matching.grok_re_preprocess(regexp)
        compiled = regex.compile(grokked_re)
        self.assertDictEqual(
            compiled.match(other_log).groupdict(),
            {"syslog_timestamp": "Mar 25 12:26:57",
             "host": 'myserver.io',
             "remote_addr": '62.73.84.230',
             "remote_user": None,
             "time_local": "25/Mar/2016:12:26:57 +0000",
             "method": "GET",
             "path": "/orders",
             "params": "?order_identifier=AB075081&consumer_name=&consumer_first_name=",
             "httpversion": "1.1",
             "status": "200",
             "body_bytes_sent": "1499",
             "http_user_agent": '"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36"'
            })

class PatternTraverserTests(unittest.TestCase):

    def test_collect_types(self):
        traverser = pattern_matching.PatternTraverser()
        re = regex.sub(pattern_matching.GROK_REPLACE_PATTERN,
                       traverser.sub_pattern,
                       'This is process %{POSINT:processid:int} running in %{PATH:process_dir}')
        self.assertDictEqual(traverser.pattern_types, {'processid': int})


class TestTypeCollection(unittest.TestCase):

    def test_convert_fields(self):
        type_collection = pattern_matching.TypeCollection({'age': int})
        self.assertDictEqual(
            type_collection.convert_fields({'age': '45'}),
            {'age': 45}
        )

    def test_convert_fields_empty(self):
        type_collection = pattern_matching.TypeCollection({'age': int})
        self.assertDictEqual(type_collection.convert_fields({}), {})

    def test_convert_fields_none(self):
        type_collection = pattern_matching.TypeCollection({'age': int})
        self.assertIsNone(type_collection.convert_fields(None))
