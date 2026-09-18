PYTHON ?= python3

.PHONY: setup lint test validate verify-golden sample evidence verify secret-scan docker-smoke

setup:
	$(PYTHON) -m pip install pip==26.2.1
	$(PYTHON) -m pip install -e '.[dev]'

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

test:
	$(PYTHON) -m pytest

validate:
	$(PYTHON) scripts/validate_task_packages.py
	$(PYTHON) scripts/validate_structured_files.py
	$(PYTHON) scripts/check_markdown_links.py

verify-golden:
	$(PYTHON) scripts/verify_golden_patches.py

sample:
	$(PYTHON) scripts/run_episode.py tasks/bug_fixing/python-retry-backoff --golden --output reports/generated/sample

evidence:
	$(PYTHON) scripts/generate_evidence_summary.py

secret-scan:
	$(PYTHON) scripts/secret_scan.py

verify: lint test validate verify-golden sample evidence secret-scan

docker-smoke:
	docker compose build
	docker compose up --abort-on-container-exit --exit-code-from lab

.PHONY: verify-protocol
verify-protocol:
	$(PYTHON) -m pytest tests/protocol_bench
