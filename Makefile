.PHONY: verify-all test build dev

verify-all:
	python scripts/verify_all.py

test:
	pytest tests -q

build:
	npm run build --prefix frontend
