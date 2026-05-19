UV = uv
PYTHON = $(UV) run python3
MODULE = src

install:
	$(UV) sync

run:
	$(PYTHON) -m $(MODULE)

debug:
	$(PYTHON) -m pdb -m $(MODULE)

clean:
	rm -rf __pycache__
	rm -rf $(MODULE)/__pycache__
	rm -rf .mypy_cache_

fclean: clean
	rm -rf .venv

lint:
	$(UV) run flake8 $(MODULE)
	$(UV) run mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs $(MODULE)

lint-strict:
	$(UV) run flake8 $(MODULE)
	$(UV) run mypy --strict $(MODULE)

re: fclean install

.PHONY: all install run debug clean fclean lint lint-strict
