# run the app in development mode
dev:
  rye run  uvicorn src.app:app --reload --port 8000

# install project using rye
install:
  rye sync -f

# run test with pytest
test query="." *args='':
  rye run pytest tests -k {{query}} --tb=short --show-capture stdout {{args}}

# generate the documentation
docs:
  rye run mkdocs serve

# run all quality checks
quality:
  rye run pyright src
  rye run ruff check src
