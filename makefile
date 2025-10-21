.PHONY: venv run

venv:
	if not exist .venv uv venv

run: venv
	.venv\Scripts\activate && python main.py
