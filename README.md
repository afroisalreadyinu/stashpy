## What is this?

Stashpy aims to be a slimmed-down Python 3 replacement for
[Logstash](https://www.elastic.co/products/logstash), a log
aggregator. Stashpy accepts connections on a TCP port. Messages passed
to it over such a connection are parsed according to a user-defined
configuration, and indexed on an ElasticSearch cluster.

Stashpy is still in development.

## Installing

In order to use Stashpy, you first need Python 3 on your system. All linux distros have a relatively new version in their official repositories. On Mac OS, the Homebrew version is recommended. Python 3 comes with pyvenv, a built-in version of virtualenv. Stashpy is [on PyPI](https://pypi.python.org/pypi/stashpy), so you can
simply install it as a dependency, or with `pip install stashpy`.

**Local**:  You are advised to use pyvenv/virtualenv/virtualenvwrapper.

**Server**: Install Stashpy in `/opt/stashpy` by creating a virtualenv
  there.

## Running

Locally, install inside a virtualenv and call the `stashpy` command.

On a server, use the sample `stashpy.conf` upstart configuration.
Unfortunately, we haven't moved on to systemd yet, so no sample
configuration for that, but it shouldn't be too difficult.

## Usage

Start with `stashpy sample-config.yml`. As can be seen from the
extension, the configuration format is YAML.

The obvious configuration options are as follows:

* `address`, `port`: The address and port on which Stashpy should listen.

* `indexer_config`
