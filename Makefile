.PHONY: run dev install kill test-health test-parse test-parse-2 ngrok freeze help

VENV = venv/bin
PORT ?= 3000

## Start server (production mode)
run:
	$(VENV)/uvicorn app:app --host 0.0.0.0 --port $(PORT)

## Kill process using port $(PORT)
kill:
	@lsof -ti :$(PORT) | xargs kill -9 && echo "Port $(PORT) freed" || echo "Port $(PORT) sudah kosong"

## Start server with auto-reload (development)
dev:
	$(VENV)/uvicorn app:app --reload --port $(PORT)

## Create venv and install all dependencies
install:
	python3 -m venv venv
	$(VENV)/pip install --upgrade pip
	$(VENV)/pip install -r requirements.txt

## Check health endpoint
test-health:
	curl -s http://localhost:$(PORT)/health | python3 -m json.tool

## Test expense message parsing
test-parse:
	curl -s -X POST http://localhost:$(PORT)/test/parse \
		-H "Content-Type: application/json" \
		-d '{"message": "Makan siang warteg 15rb cash"}' | python3 -m json.tool

test-parse-2:
	curl -s -X POST http://localhost:$(PORT)/test/parse \
		-H "Content-Type: application/json" \
		-d '{"message": "Grab ke kantor 32rb gopay tadi pagi"}' | python3 -m json.tool

## Expose local port via ngrok
ngrok:
	ngrok http $(PORT)

## Pin current venv packages to requirements.txt
freeze:
	$(VENV)/pip freeze > requirements.txt

help:
	@echo ""
	@echo "  make dev          - Start server with auto-reload"
	@echo "  make run          - Start production server"
	@echo "  make install      - Create venv and install dependencies"
	@echo "  make kill         - Free port 3000"
	@echo "  make test-health  - Check health endpoint"
	@echo "  make test-parse   - Test expense message parsing"
	@echo "  make ngrok        - Expose port via ngrok"
	@echo "  make freeze       - Pin packages to requirements.txt"
	@echo ""
