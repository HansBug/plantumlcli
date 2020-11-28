import os
from typing import Callable

from plantumlcli.utils import all_func

_env = os.environ

DEMO_PATH = _env.get('DEMO_PATH', None)
DEMO_JAR_PATH = _env.get('DEMO_JAR_PATH', None)

DEAD_FILE_PATH = _env.get('DEAD_FILE_PATH', None)
DEAD_PATH = _env.get('DEAD_PATH', None)

PRIMARY_JAR_VERSION = _env.get('PRIMARY_JAR_VERSION', None)
PRIMARY_JAR_PATH = _env.get('PRIMARY_JAR_PATH', None)

ASSISTANT_JAR_VERSION = _env.get('ASSISTANT_JAR_VERSION', None)
ASSISTANT_JAR_PATH = _env.get('ASSISTANT_JAR_PATH', None)

BROKEN_JAR_PATH = _env.get('BROKEN_JAR_PATH', None)
INVALID_JAR_PATH = _env.get('INVALID_JAR_PATH', None)

TEST_PLANTUML_HOST = _env.get('TEST_PLANTUML_HOST', None)

DEMO_HELLOWORLD_PUML = _env.get('DEMO_HELLOWORLD_PUML', None)
DEMO_COMMON_PUML = _env.get('DEMO_COMMON_PUML', None)
DEMO_CHINESE_PUML = _env.get('DEMO_CHINESE_PUML', None)
DEMO_LARGE_PUML = _env.get('DEMO_LARGE_PUML', None)


def exist_func(var) -> Callable[[], bool]:
    return all_func(lambda: var)


def path_exist_func(var) -> Callable[[], bool]:
    return all_func(exist_func(var), lambda: os.path.exists(var))


def is_file_func(var) -> Callable[[], bool]:
    return all_func(path_exist_func(var), lambda: os.path.isfile(var))


def is_dir_func(var) -> Callable[[], bool]:
    return all_func(path_exist_func(var), lambda: os.path.isdir(var))
