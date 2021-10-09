.PHONY: docs pdocs test unittest benchmark

WORKERS  ?=
RERUN    ?=

PROJ_DIR := $(shell readlink -f ${CURDIR})

DOC_DIR  := ${PROJ_DIR}/docs
TEST_DIR := ${PROJ_DIR}/test
SRC_DIR  := ${PROJ_DIR}/plantumlcli

RANGE_DIR      ?= .
RANGE_TEST_DIR := ${TEST_DIR}/${RANGE_DIR}
RANGE_SRC_DIR  := ${SRC_DIR}/${RANGE_DIR}

CI_DEFAULT_RERUNS       := 5
CI_DEFAULT_RERUNS_DELAY := 10
DEFAULT_RERUNS          := 3
DEFAULT_RERUNS_DELAY    := 5
RERUNS                  ?= $(if ${CI},${CI_DEFAULT_RERUNS},${DEFAULT_RERUNS})
RERUNS_DELAY            ?= $(if ${CI},${CI_DEFAULT_RERUNS_DELAY},${DEFAULT_RERUNS_DELAY})

COV_TYPES ?= xml term-missing

test: unittest

unittest:
	pytest "${RANGE_TEST_DIR}" \
		-sv -m unittest \
		$(shell for type in ${COV_TYPES}; do echo "--cov-report=$$type"; done) \
		--cov="${RANGE_SRC_DIR}" \
		$(if ${MIN_COVERAGE},--cov-fail-under=${MIN_COVERAGE},) \
		$(if ${WORKERS},-n ${WORKERS},) \
		--durations=10 \
		$(if ${CI}${RERUN},--reruns ${RERUNS} --reruns-delay ${RERUNS_DELAY},)

benchmark:
	pytest ${RANGE_TEST_DIR} -sv -m benchmark -n 1 --durations=0

docs:
	$(MAKE) -C "${DOC_DIR}" build
pdocs:
	$(MAKE) -C "${DOC_DIR}" prod