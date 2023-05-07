.PHONY: docs pdocs test unittest

RERUN       ?=
RERUN_DELAY ?=
TIMEOUT     ?=

PROJ_DIR := $(shell readlink -f ${CURDIR})

DOC_DIR  := ${PROJ_DIR}/docs
TEST_DIR := ${PROJ_DIR}/test
SRC_DIR  := ${PROJ_DIR}/plantumlcli

RANGE_DIR      ?= .
RANGE_TEST_DIR := ${TEST_DIR}/${RANGE_DIR}
RANGE_SRC_DIR  := ${SRC_DIR}/${RANGE_DIR}

CI_DEFAULT_RERUN          := 3
LOCAL_DEFAULT_RERUN       := 0
DEFAULT_RERUN             ?= $(if ${CI},${CI_DEFAULT_RERUN},${LOCAL_DEFAULT_RERUN})
ACTUAL_RERUN              := $(if ${RERUN},${RERUN},${DEFAULT_RERUN})

CI_DEFAULT_RERUN_DELAY    := 10
LOCAL_DEFAULT_RERUN_DELAY := 5
DEFAULT_RERUN_DELAY       ?= $(if ${CI},${CI_DEFAULT_RERUN_DELAY},${LOCAL_DEFAULT_RERUN_DELAY})
ACTUAL_RERUN_DELAY        := $(if ${RERUN_DELAY},${RERUN_DELAY},${DEFAULT_RERUN_DELAY})

CI_DEFAULT_TIMEOUT        := 30
LOCAL_DEFAULT_TIMEOUT     := 15
DEFAULT_TIMEOUT           ?= $(if ${CI},${CI_DEFAULT_TIMEOUT},${LOCAL_DEFAULT_TIMEOUT})
ACTUAL_TIMEOUT            := $(if ${TIMEOUT},${TIMEOUT},${DEFAULT_TIMEOUT})

COV_TYPES ?= xml term-missing

test: unittest

unittest:
	pytest "${RANGE_TEST_DIR}" \
		-sv -m unittest \
		$(shell for type in ${COV_TYPES}; do echo "--cov-report=$$type"; done) \
		--cov="${RANGE_SRC_DIR}" \
		$(if ${MIN_COVERAGE},--cov-fail-under=${MIN_COVERAGE},) \
		$(if ${CI}${ACTUAL_RERUN},--reruns ${ACTUAL_RERUN} --reruns-delay ${ACTUAL_RERUN_DELAY},) \
		$(if ${ACTUAL_TIMEOUT},--timeout=${ACTUAL_TIMEOUT},)

docs:
	$(MAKE) -C "${DOC_DIR}" build
pdocs:
	$(MAKE) -C "${DOC_DIR}" prod

flake:
	flake8 ./plantumlcli --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 ./plantumlcli --count --exit-zero \
		--max-complexity=10 --max-line-length=127 --statistics \
		--per-file-ignores="__init__.py:F401"
