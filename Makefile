WORKERS      ?=
RERUNS       ?= 5
RERUNS_DELAY ?= 5

TEST_DIR ?= ./test
IS_CI    := $(shell echo ${CI})

WORKERS_COMMAND = $(if ${WORKERS},-n ${WORKERS},)
RERUN_COMMAND   = $(if ${IS_CI},--reruns ${RERUNS} --reruns-delay ${RERUNS_DELAY},)

unittest:
	pytest ${TEST_DIR} \
		--cov-report term-missing --cov=./plantumlcli \
		${RERUN_COMMAND} \
		--durations=10 \
		-sv -m unittest ${WORKERS_COMMAND}

benchmark:
	pytest ${TEST_DIR} -sv -m benchmark -n 1 --durations=0
