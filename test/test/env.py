import os

_env = os.environ

DEMO_PATH = _env.get('DEMO_PATH', None)
DEMO_JAR_PATH = _env.get('DEMO_JAR_PATH', None)

PRIMARY_JAR_VERSION = _env.get('PRIMARY_JAR_VERSION', None)
PRIMARY_JAR_PATH = _env.get('PRIMARY_JAR_PATH', None)

ASSISTANT_JAR_VERSION = _env.get('ASSISTANT_JAR_VERSION', None)
ASSISTANT_JAR_PATH = _env.get('ASSISTANT_JAR_PATH', None)
