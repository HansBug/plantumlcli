# plantumlcli

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code Lint](https://github.com/HansBug/plantumlcli/workflows/Code%20Lint/badge.svg)](https://github.com/HansBug/plantumlcli/actions?query=workflow%3A%22Code+Lint%22)
[![Code Test](https://github.com/HansBug/plantumlcli/workflows/Code%20Test/badge.svg)](https://github.com/HansBug/plantumlcli/actions?query=workflow%3A%22Code+Test%22)
[![Coverage Status](https://coveralls.io/repos/github/HansBug/plantumlcli/badge.svg?branch=main)](https://coveralls.io/github/HansBug/plantumlcli?branch=main)

Python cli and package interface for local and remote plantuml

## Install

Install from official pypi

```bash
pip install plantumlcli  # not online yet, do not use
```

Install from source code

```bash
git clone https://github.com/HansBug/plantumlcli
cd plantumlcli && pip install .
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

In default, no local plantuml jar can be used, the remote host is set to the official one (http://www.plantuml.com/plantuml). But don't worry, you can specify your plantuml jar file or remote host by environment variables or command lines.

```bash
plantumlcli -c                                             # local not okay, remote is okay
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

You can also get the URL address of remote plantuml (in these cases, remote plantuml will be used regardless of `-L` and `-R` commands)

```bash
plantumlcli -u helloworld.puml              # get png URL of helloworld.puml
plantumlcli -u -t eps helloworld.puml       # get eps URL of helloworld.puml
plantumlcli --homepage-url helloworld.puml  # get online editor's URL of helloworld.puml
plantumlcli -u helloworld.puml common.puml  # get png URL of the 2 puml files (one line for one URL, in order)
```

## Using from python

(not complete yet)

TODO : Complete this part, make some examples