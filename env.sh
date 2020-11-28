#!/bin/bash

# global configuration
if [ -z "${DEMO_PATH}" ]; then
  export DEMO_PATH="demo"
fi
if [ ! -d ${DEMO_PATH} ]; then
  git clone "https://github.com/HansBug/plantumlcli-testfile.git" ${DEMO_PATH}
fi

export DEAD_FILE_PATH="${DEMO_PATH}/dead_file"
touch ${DEAD_FILE_PATH}
chmod 000 ${DEAD_FILE_PATH}

export DEAD_PATH="${DEMO_PATH}/dead_path"
mkdir -p ${DEAD_PATH}
chmod 000 ${DEAD_PATH}

# demo/jar configuration
export DEMO_JAR_PATH="${DEMO_PATH}/jar"
mkdir -p ${DEMO_JAR_PATH}

if [ -z "${PRIMARY_JAR_VERSION}" ]; then
  export PRIMARY_JAR_VERSION="1.2020.19"
fi
export PRIMARY_JAR_PATH="${DEMO_JAR_PATH}/plantuml.${PRIMARY_JAR_VERSION}.jar"

if [ -z "${ASSISTANT_JAR_VERSION}" ]; then
  export ASSISTANT_JAR_VERSION="1.2020.16"
fi
export ASSISTANT_JAR_PATH="${DEMO_JAR_PATH}/plantuml.${ASSISTANT_JAR_VERSION}.jar"

export BROKEN_JAR_PATH="${DEMO_JAR_PATH}/broken.jar"
export INVALID_JAR_PATH="${DEMO_JAR_PATH}/helloworld.jar"

# test host configuration
# there should be a TEST_PLANTUML_HOST here, defined outside

# puml demo configuration
export DEMO_UML_PATH="${DEMO_PATH}/uml"

export DEMO_HELLOWORLD_PUML="${DEMO_UML_PATH}/helloworld.puml"
export DEMO_COMMON_PUML="${DEMO_UML_PATH}/common.puml"
export DEMO_CHINESE_PUML="${DEMO_UML_PATH}/chinese.puml"
export DEMO_LARGE_PUML="${DEMO_UML_PATH}/large.puml"
