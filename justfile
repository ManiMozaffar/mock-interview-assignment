dev: # run the app in development mode
  rye run  uvicorn src.app:app --reload --port 8000

test query="." *args='': # run test with pytest
  rye run pytest tests -k {{query}} --tb=short --show-capture stdout {{args}}

docs: # generate the documentation
  rye run mkdocs serve

quality: # run all quality checks
  rye run pyright src
  rye run ruff check src
