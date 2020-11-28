WORKERS      ?= 1
RERUNS       ?= 5
RERUNS_DELAY ?= 5

unittest:
	pytest ./test \
		--cov-report term-missing --cov=./plantumlcli \
		--reruns ${RERUNS} --reruns-delay ${RERUNS_DELAY} --only-rerun requests.exceptions.HTTPError \
		--durations=10 \
		-sv -m unittest -n ${WORKERS}

benchmark:
	pytest ./test -sv -m benchmark -n 1 --durations=0
