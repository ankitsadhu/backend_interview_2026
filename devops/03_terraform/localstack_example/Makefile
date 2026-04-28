.PHONY: up-localstack bootstrap up smoke clean-local logs down

up-localstack:
	docker compose up -d localstack

bootstrap:
	./scripts/bootstrap_localstack.sh

up:
	docker compose up --build app worker

smoke:
	./scripts/smoke_test.sh

clean-local:
	./scripts/clean_localstack.sh

logs:
	docker compose logs -f

down:
	docker compose down

