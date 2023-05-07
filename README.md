# plantumlcli

[![PyPI](https://img.shields.io/pypi/v/plantumlcli)](https://pypi.org/project/plantumlcli/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/plantumlcli)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/plantumlcli)
![Loc](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/HansBug/b0362248ec0e7574ab22ea80df775197/raw/loc.json)
![Comments](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/HansBug/b0362248ec0e7574ab22ea80df775197/raw/comments.json)

[![Docs Deploy](https://github.com/hansbug/plantumlcli/workflows/Docs%20Deploy/badge.svg)](https://github.com/hansbug/plantumlcli/actions?query=workflow%3A%22Docs+Deploy%22)
[![Code Test](https://github.com/hansbug/plantumlcli/workflows/Code%20Test/badge.svg)](https://github.com/hansbug/plantumlcli/actions?query=workflow%3A%22Code+Test%22)
[![Badge Creation](https://github.com/hansbug/plantumlcli/workflows/Badge%20Creation/badge.svg)](https://github.com/hansbug/plantumlcli/actions?query=workflow%3A%22Badge+Creation%22)
[![Package Release](https://github.com/hansbug/plantumlcli/workflows/Package%20Release/badge.svg)](https://github.com/hansbug/plantumlcli/actions?query=workflow%3A%22Package+Release%22)
[![codecov](https://codecov.io/gh/hansbug/plantumlcli/branch/main/graph/badge.svg?token=XJVDP4EFAT)](https://codecov.io/gh/hansbug/plantumlcli)

[![GitHub stars](https://img.shields.io/github/stars/hansbug/plantumlcli)](https://github.com/hansbug/plantumlcli/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/hansbug/plantumlcli)](https://github.com/hansbug/plantumlcli/network)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/hansbug/plantumlcli)
[![GitHub issues](https://img.shields.io/github/issues/hansbug/plantumlcli)](https://github.com/hansbug/plantumlcli/issues)
[![GitHub pulls](https://img.shields.io/github/issues-pr/hansbug/plantumlcli)](https://github.com/hansbug/plantumlcli/pulls)
[![Contributors](https://img.shields.io/github/contributors/hansbug/plantumlcli)](https://github.com/hansbug/plantumlcli/graphs/contributors)
[![GitHub license](https://img.shields.io/github/license/hansbug/plantumlcli)](https://github.com/hansbug/plantumlcli/blob/master/LICENSE)

An easy-to-use plantuml cli for everyone.

## Install

Install from official pypi

```bash
pip install plantumlcli
```

Install from source code

```bash
git clone https://github.com/HansBug/plantumlcli
cd plantumlcli && pip install .
```

Python 3.7+ is required, pypy is also tested to be okay.

If you need to export the diagrams to PDF format, just install like this

```bash
pip install plantumlcli[pdf]
```

## Using with cli

### Basic Usage

Show version of `plantumlcli`

```bash
plantumlcli -v
```

Show help information of `plantumlcli`

```bash
plantumlcli -h
```

Check the local plantuml environment and remote plantuml host

```bash
plantumlcli -c   # check both environments
plantumlcli -cL  # check local environment only
plantumlcli -cR  # check remote environment only
```

In default, no local plantuml jar can be used, the remote host is set to the official
one (http://www.plantuml.com/plantuml). But don't worry, you can specify your plantuml jar file or remote host by
environment variables or command lines.

```bash
plantumlcli -c                                             # local not okay, remote okay
PLANTUML_HOST=http://plantuml.example.com plantumlcli -cR  # remote okay
plantumlcli -cR -r http://plantuml.example.com             # remote okay
PLANTUML_JAR=/my/path/plantuml.jar plantumlcli -cL         # local okay
plantumlcli -cL -p /my/path/plantuml.jar                   # local okay
```

Build image from plantuml source code

```bash
plantumlcli source.puml                # the target image will be named as 'source.png'
plantumlcli -o image.png source.puml   # the target image will be named as 'image.png'
plantumlcli -t eps source.puml         # eps format is supported
plantumlcli source1.puml source2.puml  # 2 source codes, the images' names will be 'source1.png' and 'source2.png'
plantumlcli -o image1.png -o image2.png source1.puml source2.puml  # 2 source codes, image will be 'image1.png' and 'image2.png'

PLANTUML_JAR=/my/path/plantuml.jar plantumlcli source.puml     # use local plantuml jar to build png
PLANTUML_JAR=/my/path/plantuml.jar plantumlcli -L source.puml  # force use local plantuml jar to build png
PLANTUML_HOST=http://plantuml.example.com plantuml source.puml     # use your plantuml host to build png
PLANTUML_HOST=http://plantuml.example.com plantuml -R source.puml  # force use your plantuml host to build png
```

You can also get the URL address of remote plantuml (in these cases, remote plantuml will be used regardless of `-L`
and `-R` commands)

```bash
plantumlcli -u helloworld.puml              # get png URL of helloworld.puml
plantumlcli -u -t eps helloworld.puml       # get eps URL of helloworld.puml
plantumlcli --homepage-url helloworld.puml  # get online editor's URL of helloworld.puml
plantumlcli -u helloworld.puml common.puml  # get png URL of the 2 puml files (one line for one URL, in order)
```

## Using from python

You can also use plantumlcli in python source code by `import`

```python
# environment variables
# PLANTUML_JAR=/path/to/plantuml.jar
# PLANTUML_HOST=https://plantuml.example.com

from pathlib import Path
from plantumlcli import LocalPlantuml, RemotePlantuml

if __name__ == "__main__":
    code = Path('source.puml').read_text()

    local = LocalPlantuml.autoload()
    print(local.dump_txt(code))  # print text graph of code
    local.dump('/my/path/source_local.png', 'png', code)  # save png to /my/path/source_local.png
    local.dump('/my/path/source_local.eps', 'eps', code)  # save eps to /my/path/source_local.eps

    remote = RemotePlantuml.autoload()
    print(remote.dump_txt(code))  # print text graph of code
    remote.dump('/my/path/source_remote.png', 'png', code)  # save png to /my/path/source_remote.png
    remote.dump('/my/path/source_remote.eps', 'eps', code)  # save eps to /my/path/source_remote.eps
    print(remote.get_url('png', code))  # get png url from remote host
    print(remote.get_homepage_url(code))  # get online editor's url from remote host

```

## Contributing

Thank you for considering contributing to plantumlcli!

We appreciate all contributions to improve plantumlcli, both logic and system designs. Please refer to CONTRIBUTING.md
for more guides.

And users can join
our [slack communication channel](https://join.slack.com/t/hansbug/shared_invite/zt-z3rtyooz-Rf6QZ9eNy6t5vvUGnicfdw), or
contact the core developer [HansBug](https://github.com/HansBug) for more detailed discussion.

## Links

Github: [https://github.com/HansBug/plantumlcli](https://github.com/HansBug/plantumlcli)

Documentation(just readme yet, will be written
soon): [https://github.com/HansBug/plantumlcli/blob/main/README.md](https://github.com/HansBug/plantumlcli/blob/main/README.md)

Issue Tracker: [https://github.com/HansBug/plantumlcli/issues](https://github.com/HansBug/plantumlcli/issues)

Pypi: [https://pypi.org/project/plantumlcli/](https://pypi.org/project/plantumlcli/)

Test pypi(pre-released versions can be found
here): [https://test.pypi.org/project/plantumlcli/](https://test.pypi.org/project/plantumlcli/)

## Change log

### Version 0.0.3

Released 2021-10-8

* Fix the problem when using official site.
* click version requirement changed to >= 7.0, will not conflict with other packages any more.

### Version 0.0.2

Released 2020-11-30

* Fix a bug on windows platform,
  issue: [https://github.com/HansBug/plantumlcli/issues/1](https://github.com/HansBug/plantumlcli/issues/1)

### Version 0.0.1

Released 2020-11-29

* The first official `plantumlcli` version, cheers!!! :beers:

