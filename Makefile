.PHONY: dev
dev: ## Install dev dependencies
	uv sync --dev

.PHONY: install
install: 
	uv sync

.PHONY: test
test:  ## Run tests
	uv run pytest

.PHONY: test-dev
test:  ## Run tests
	uv run pytest -vv  -s

.PHONY: lint
lint:  ## Run linters
	uv run ruff check

.PHONY: fix
fix:  ## Fix lint errors
	uv run ruff check --fix

.PHONY: cov
cov: ## Run tests with coverage
	uv run pytest

.PHONY: build
build:  ## Build package
	uv build
