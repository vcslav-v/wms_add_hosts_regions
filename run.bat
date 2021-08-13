pip3 install poetry
poetry config virtualenvs.in-project true
poetry install --no-dev
poetry run python main.py