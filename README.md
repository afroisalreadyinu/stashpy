## What is this?

Stashpy aims to be a slimmed-down Python 3 replacement for
[Logstash](https://www.elastic.co/products/logstash), a log
aggregator. Stashpy accepts connections on a TCP port. Messages passed
to it over such a connection are parsed according to a user-defined
configuration, and indexed on an ElasticSearch cluster.

Stashpy is still in development.

## Installing

In order to use Stashpy, you first need Python 3 on your system. All
linux distros have a relatively new version in their official
repositories. On Mac OS, the Homebrew version is recommended. In
addition to Python 3, you will need virtualenv. Python 3.5 comes with
pyvenv, which is a built-in equivalent of virtualenv. For earlier
versions, you will need to manually install virtualenv with `sudo pip
install virtualenv. If you already have a 2.* version of Python
installed together with virtualenv, you can install Python 3 and call
virtualenv with the `--python` argument to use the new version, as in
`virtualenv stashpy --python \`which python3.4\``.

Stashpy is [on PyPI](https://pypi.python.org/pypi/stashpy), so you can
simply install it as a dependency, or with `pip install stashpy`. For
development purposes, you can simply create a virtualenv wherever you
prefer, and run Stashpy from there.

The recommended way to run Stashpy as a service on a server is by
checking it out into `/opt`, and also creating a virtualenv
there. First install the above mentioned dependencies. Then run `cd
/opt && git clone git@github.com:afroisalreadyinu/stashpy.git` as
root. Afterwards, create the virtualenv with `virtualenv
/opt/stashpy`, again as root.

You can modify the provided `stashpy.conf` to use as an upstart
config.

## Running

The entry point is named `stashpy`, and accepts a configuration file
as the only argument. A sample configuration file `sample-config.yml`
is provided. See the Usage section for documentation on different
configuration options.

On a server, use the sample `stashpy.conf` upstart configuration.
Unfortunately, we haven't moved on to systemd yet, so no sample
configuration for that, but it shouldn't be too difficult.

## Usage

Start with `stashpy sample-config.yml`. As can be seen from the
extension, the configuration format is YAML.

The obvious configuration options are as follows:

* `address`, `port`: The address and port on which Stashpy should listen.

* `indexer_config`:

  - `host`: ElasticSearch host

  - `port`: ES port

  - `index_pattern`: The base pattern to be used for determining index
    name. This pattern will be passed on to
    [`datetime.strftime`](https://docs.python.org/3/library/datetime.html#datetime.date.strftime),
    and will then be formatted with the parsed values dictionary.

* `logging`: This configuration option will be passed on as-is to the
  `logging.config.dictConfig` method. If it is not supplied,
  `stashpy.main.DEFAULT_LOGGING` will be used.

* `processor_spec`: The parsing specification. See the next section
  for details.

## Parsing Specification

Stashpy turns lines (i.e. strings that end with a newline) that are
supplied through a TCP connection into dictionaries, and indexes these
in ElasticSearch. There are two methods you can use to specify how to
go from log lines to dictionaries.

### Using `to_dict` and `to_format`

The first is by providing the `processor_spec` option in the
configuration file. This option can have two keys:

* `to_dict`: A list of strings that are used to turn log lines into
  dictionaries.

* `to_format`: A list of dictionaries whose keys are parsing strings,
  and values are dictionariers that are to be formatted based on
  parsed values.

For both, the specification can be either in the format specification,
parsed using the [parse library](https://pypi.python.org/pypi/parse),
or a regular expression with named patterns. For example, the
following are equivalent ways of parsing the same pattern:

* `My name is {name} and I'm {age:d} years old.`

* `My name is (?P<name>\w*) and I'm (?P<age>\d*) years old\.`

Either of these patterns, when included as an element of `to_dict`,
will parse the sentence `My name is Yuri and I'm 25 years old.`. The
first one will result in the following Python dictionary:

    {"name": "Yuri", "age": 25}

The second line, however, will not provide a conversion of the `age`
value into an integer, and will result in the following:

    {"name": "Yuri", "age": "25"}

If you want the parsed data to be subject to further modification and
conversion, have a look at class-based processing below.

The `to_format` option requires the formatting dictionary to be
specified as the value for the parsing specification key. In the
configuration, it would look like this:

    to_format:
      "Her name is {name} and she's {age:d} years old.":
        name_line: "Name is {name}"
        age_line: "Age is {age}"

As you can see, all values in this dictionary are interpolated as
strings.

### Custom class

The second method of processing log lines is by specifying a class
that is responsible for accepting them and returning dictionaries. The
path of this class can be passed using the `processor_class`
option. This class must subclass `stashpy.LineProcessor` and implement
the method `for_line(self, line)`, which will be called for each log
line. Two useful methods from the parent class that can be used for
more specialized processing are `do_dict_specs(self, line)`, and
`do_format_specs`. The first method returns the result for the first
match from the `self.dict_specs` list, while the second does the same
for the `self.format_specs` attribute. If your class has the class
attributes `TO_DICT` or `TO_FORMAT`, these will be used to populate
the instance attributes. The following example is equivalent to what
happens in the default processing pipeline:


### Processing pipeline

The order of processing in Stashpy is relatively
straightforward. First, the `to_dict` specs are applied; if any of the
patterns match, the resulting dictionary is returned. If there are no
such matches, the `to_format` specs are applied, and the result from
the first match is returned. If you are using a custom class for
processing, you can introduce your own ordering and logic.

## Testing

One thing that really annoyed me about Logstash was that testing
patterns was incredibly difficult; the only reliable test could be
done on the live system. Stashpy aims to make testing patterns
simpler. In order to test a parsing specification, simply subclass
`stashpy.tests.PatternTest`. This class has three methods that can be
used to process a logline with a parsing specification:

* `process_to_dict(self, to_dict_spec, logline)`: Processes a list of
  to dictionary parsing specifications, and returns result.

* `process_to_format(self, to_format_spec, logline)`: Processes a list
  of to format parsing specifications, and returns result.

Here is a sample test:
```python
import unittest

from stashpy.tests import PatternTest

class SampleTest(PatternTest):

    def test_pattern(self):
        self.assertDictEqual(
            self.process_to_dict(["My name is {name} and I'm {age:d} years old."],
                                 "My name is Yuri and I'm 3 years old."),
            {'name': 'Yuri', 'age': 3})

if __name__ == '__main__':
    unittest.main()
```