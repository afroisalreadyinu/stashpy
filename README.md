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

TBW