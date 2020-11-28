WORKERS ?= 1

unittest:
	pytest ./test --cov-report term-missing --cov=./plantumlcli -sv -m unittest -n ${WORKERS} --durations=10

benchmark:
	pytest ./test -sv -m benchmark -n 1 --durations=0
