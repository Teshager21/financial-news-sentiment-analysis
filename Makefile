# Variables
VENV_NAME := venv
PYTHON := $(VENV_NAME)/bin/python
PIP := $(VENV_NAME)/bin/pip

# Auto-detect dependency manager if not explicitly set
ifeq ($(origin DEP_MANAGER), undefined)
	ifneq ("$(wildcard pyproject.toml)","")
		# Check if pyproject.toml contains [tool.poetry]
		DEP_MANAGER := poetry
		ifneq ($(shell grep -q '\[tool.poetry\]' pyproject.toml && echo yes),yes)
			DEP_MANAGER := requirements
		endif
	else ifneq ("$(wildcard Pipfile)","")
		DEP_MANAGER := pipenv
	else
		DEP_MANAGER := requirements
	endif
endif

.PHONY: help
help:
	@echo "Usage:"
	@echo "  make init [DEP_MANAGER=poetry|pipenv|requirements]  Create env and install dependencies"
	@echo "  make lint [DEP_MANAGER=...]                         Run linting"
	@echo "  make format [DEP_MANAGER=...]                       Format code"
	@echo "  make test [DEP_MANAGER=...]                         Run tests"
	@echo "  make clean                                         Remove build artifacts"
	@echo "  make fix-deps [DEP_MANAGER=...]                     Recreate env and reinstall dependencies"
	@echo ""
	@echo "Detected DEP_MANAGER = $(DEP_MANAGER)"

.PHONY: init
init:
	@echo "Using dependency manager: $(DEP_MANAGER)"
	@echo "🔧 Cleaning up previous build artifacts..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf dist build *.egg-info __pycache__

ifeq ($(DEP_MANAGER), poetry)
	@echo "🐍 Installing dependencies with Poetry..."
	poetry install
endif

ifeq ($(DEP_MANAGER), requirements)
	@if [ ! -d $(VENV_NAME) ]; then \
		echo "🐍 Creating virtual environment..."; \
		python3 -m venv $(VENV_NAME); \
	fi
	@echo "📦 Installing dependencies from requirements files..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r dev-requirements.txt
endif

ifeq ($(DEP_MANAGER), pipenv)
	@echo "📦 Installing dependencies with Pipenv..."
	pipenv install --dev
endif

	@echo "🔁 Checking for pre-commit config..."
	@if [ ! -f .pre-commit-config.yaml ]; then \
		echo "⚠️ Warning: .pre-commit-config.yaml not found. Please ensure it exists."; \
	fi

	@echo "🔧 Ensuring Git is initialized..."
	@if [ ! -d .git ]; then \
		echo "🧰 Git repo not found. Initializing..."; \
		git init --initial-branch=main; \
		git add .; \
		git commit -m 'Initial commit'; \
	fi

	@echo "🔧 Installing pre-commit hooks..."
ifeq ($(DEP_MANAGER), poetry)
	poetry run pre-commit install
	poetry run pre-commit run --all-files || true
else ifeq ($(DEP_MANAGER), requirements)
	$(VENV_NAME)/bin/pre-commit install
	$(VENV_NAME)/bin/pre-commit run --all-files || true
else ifeq ($(DEP_MANAGER), pipenv)
	pipenv run pre-commit install
	pipenv run pre-commit run --all-files || true
endif

	@echo "✅ Setup complete."
ifeq ($(DEP_MANAGER), requirements)
	@echo "👉 Please run: source $(VENV_NAME)/bin/activate"
else
	@echo "👉 Use your dependency manager's shell or activate your environment accordingly."
endif

.PHONY: clean
clean:
	@echo "🧹 Cleaning project..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf dist build *.egg-info __pycache__ $(VENV_NAME)
	@echo "✅ Cleanup complete."

.PHONY: lint
lint:
	@echo "Using dependency manager: $(DEP_MANAGER)"
ifeq ($(DEP_MANAGER), poetry)
	poetry run flake8 src tests
endif
ifeq ($(DEP_MANAGER), pipenv)
	pipenv run flake8 src tests
endif
ifeq ($(DEP_MANAGER), requirements)
	$(VENV_NAME)/bin/flake8 src tests
endif
	@echo "✅ Linting complete."

.PHONY: format
format:
	@echo "Using dependency manager: $(DEP_MANAGER)"
ifeq ($(DEP_MANAGER), poetry)
	poetry run black src tests
	poetry run isort src tests
endif
ifeq ($(DEP_MANAGER), pipenv)
	pipenv run black src tests
	pipenv run isort src tests
endif
ifeq ($(DEP_MANAGER), requirements)
	$(VENV_NAME)/bin/black src tests
	$(VENV_NAME)/bin/isort src tests
endif
	@echo "✅ Formatting complete."

.PHONY: test
test:
	@echo "Using dependency manager: $(DEP_MANAGER)"
ifeq ($(DEP_MANAGER), poetry)
	poetry run pytest tests
endif
ifeq ($(DEP_MANAGER), pipenv)
	pipenv run pytest tests
endif
ifeq ($(DEP_MANAGER), requirements)
	-$(VENV_NAME)/bin/pytest tests || test $$? = 5
endif
	@echo "✅ Tests complete."

.PHONY: fix-deps
fix-deps:
	@echo "🔧 Fixing dependency issues..."
	make clean
	make init DEP_MANAGER=$(DEP_MANAGER)
	@echo "✅ Fix-deps complete."
