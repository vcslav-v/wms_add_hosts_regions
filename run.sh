#!/bin/bash
pip3 install poetry
poetry config virtualenvs.in-project true
poetry install --no-dev
chmod +x main.py
poetry run $(pwd)/main.py