.PHONY: fmt check test

fmt:
	poetry run black -C .
	poetry run ruff --fix .

check:
	poetry run black -C . --check
	poetry run ruff .
	# poetry run mypy src

test:
	PYTHONDEVMODE=1 poetry run pytest \
		-vvv -s --cov=geopip --cov-branch \
		--cov-report=term-missing:skip-covered \
		--cov-report=xml:coverage.xml \
		tests/
