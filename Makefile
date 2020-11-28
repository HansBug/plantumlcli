WORKERS      ?= 1
RERUNS       ?= 5
RERUNS_DELAY ?= 5

TEST_DIR ?= ./test

unittest:
	pytest ${TEST_DIR} \
		--cov-report term-missing --cov=./plantumlcli \
		--reruns ${RERUNS} --reruns-delay ${RERUNS_DELAY} \
		--only-rerun requests.exceptions.HTTPError \
		--durations=10 \
		-sv -m unittest -n ${WORKERS}

benchmark:
	pytest ${TEST_DIR} -sv -m benchmark -n 1 --durations=0
