import unittest
from stashpy import pattern_matching


class GrokPatternTests(unittest.TestCase):

    def test_normal_re(self):
        #A pattern without oniguruma patterns should work
        regexp = "My name is (?P<name>\w*) and I'm (?P<age>\d*) years old\."
        compiled = pattern_matching.compile(regexp)
        self.assertDictEqual(
            compiled.match("My name is Takeshi and I'm 4 years old.").groupdict(),
            {"name": "Takeshi", "age": '4'})

    def test_simple(self):
        regexp = "My name is %{USERNAME:name} and I'm %{INT:age} years old"
        compiled = pattern_matching.compile(regexp)
        self.assertDictEqual(
            compiled.match("My name is Takeshi and I'm 4 years old.").groupdict(),
            {"name": "Takeshi", "age": '4'})


    def test_skip_pattern(self):
        regexp = "My name is %{USERNAME:name} and I'm %{INT} years old"
        compiled = pattern_matching.compile(regexp)
        self.assertDictEqual(
            compiled.match("My name is Takeshi and I'm 4 years old.").groupdict(),
            {"name": "Takeshi"})

    def test_pattern_synonym(self):
        regexp = "My name is %{USER:username} and I'm %{INT} years old"
        compiled = pattern_matching.compile(regexp)
        self.assertDictEqual(
            compiled.match("My name is Takeshi and I'm 4 years old.").groupdict(),
            {"username": "Takeshi"})


    def test_embedded_patterns(self):
        regexp = "%{SYSLOGTIMESTAMP:timestamp}"
        compiled = pattern_matching.compile(regexp)
        self.assertDictEqual(
            compiled.match("Mar 23 2016 12:30:20").groupdict(),
            {"timestamp": "Mar 23 2016 12:30:20"})
