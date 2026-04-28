.PHONY: bootstrap check wiki-tree

bootstrap:
	./scripts/bootstrap-python.sh

check:
	python3 scripts/check_env.py

wiki-tree:
	find wiki -maxdepth 2 -type f | sort
