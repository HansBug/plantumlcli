WORKERS      ?=
RERUNS       ?= 5
RERUNS_DELAY ?= 5

TEST_DIR ?= ./test

WORKERS_COMMAND = $(if ${WORKERS},-n ${WORKERS},)

unittest:
	pytest ${TEST_DIR} \
		--cov-report term-missing --cov=./plantumlcli \
		--reruns ${RERUNS} --reruns-delay ${RERUNS_DELAY} \
		--only-rerun requests.exceptions.HTTPError \
		--durations=10 \
		-sv -m unittest ${WORKERS_COMMAND}

benchmark:
	pytest ${TEST_DIR} -sv -m benchmark -n 1 --durations=0
