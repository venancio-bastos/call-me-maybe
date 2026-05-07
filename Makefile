PYTHON = uv run python3
MODULE = src

install:
	uv sync

run:
	$(PYTHON) -m $(MODULE)

debug:
	$(PYTHON) -m pdb -m $(MODULE)

clean:
	rm -rf __pycache__
	rm -rf $(MODULE)/__pycache__
	rm -rf .mypy_cache_
# 	rm -rf .venv

lint:
	uv run flake8 $(MODULE)
	uv run mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs $(MODULE)

lint-strict:
	uv run flake8 $(MODULE)
	uv run mypy --strict $(MODULE)

.PHONY: all install run debug clean lint lint-strict
	