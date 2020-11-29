WORKERS  ?=
TEST_DIR ?= ./test
CI       := $(shell echo ${CI})
RERUN    ?=

CI_DEFAULT_RERUNS       := 5
CI_DEFAULT_RERUNS_DELAY := 10
DEFAULT_RERUNS          := 3
DEFAULT_RERUNS_DELAY    := 5
RERUNS                  ?= $(if ${CI},${CI_DEFAULT_RERUNS},${DEFAULT_RERUNS})
RERUNS_DELAY            ?= $(if ${CI},${CI_DEFAULT_RERUNS_DELAY},${DEFAULT_RERUNS_DELAY})

WORKERS_COMMAND = $(if ${WORKERS},-n ${WORKERS},)
RERUN_COMMAND   = $(if ${CI}${RERUN},--reruns ${RERUNS} --reruns-delay ${RERUNS_DELAY},)

unittest:
	pytest ${TEST_DIR} \
		--cov-report term-missing --cov=./plantumlcli \
		${RERUN_COMMAND} \
		--durations=10 \
		-sv -m unittest ${WORKERS_COMMAND}

benchmark:
	pytest ${TEST_DIR} -sv -m benchmark -n 1 --durations=0
