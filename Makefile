# Fraud Network Intelligence + Citizen Fraud Shield
PY := backend/.venv/Scripts/python.exe   # Windows venv; use backend/.venv/bin/python on *nix

.PHONY: help setup data train build run test docker docker-run clean

help:
	@echo "setup       full bootstrap (deps, data, CNN, platform build)  -> ./setup.sh or ./setup.ps1"
	@echo "data        regenerate synthetic reports"
	@echo "train       regenerate note dataset + train the currency CNN"
	@echo "build       build the platform UI (platform/dist)"
	@echo "run         run the platform + API on :8000"
	@echo "test        run the backend test suite"
	@echo "docker      build the single-image deployment"
	@echo "docker-run  run the image on :8000"

data:
	cd backend && $(PY) -m data.generate

train:
	cd backend && $(PY) -m cv.generate_notes && $(PY) -m cv.train

build:
	cd platform && npm install && npm run build

run:
	cd backend && $(PY) -m uvicorn app.main:app --port 8000

test:
	cd backend && $(PY) -m pytest -q

docker:
	docker build -t fraud-shield .

docker-run:
	docker run --rm -p 8000:8000 fraud-shield

clean:
	rm -rf backend/cv/data backend/cv/samples backend/cv/*.pt backend/out platform/dist
