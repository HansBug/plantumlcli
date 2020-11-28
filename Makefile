unittest:
	pytest ./test --cov-report term-missing --cov=./plantumlcli -sv -m unittest --durations=10

benchmark:
	pytest ./test -sv -m benchmark --durations=0
