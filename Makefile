.PHONY: dev

dev:
	docker-compose up --build

health:
	curl http://localhost:8000/healthz