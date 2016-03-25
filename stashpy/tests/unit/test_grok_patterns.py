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
