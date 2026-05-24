SHELL := /bin/bash

-include .env
export $(shell sed 's/=.*//' .env 2>/dev/null)

.PHONY: up down restart logs health setup-claude bootstrap test lint protect-branch sync-labels

up:
	./scripts/start.sh

down:
	./scripts/stop.sh

restart: down up

logs:
	docker compose logs -f --tail=200

health:
	./scripts/healthcheck.sh

setup-claude:
	./scripts/setup-claude.sh

bootstrap:
	./scripts/bootstrap.sh


test:
	./scripts/run-tests.sh

lint:
	for script in scripts/*.sh; do bash -n "$$script"; done
	docker compose config >/dev/null

protect-branch:
	./scripts/apply-branch-protection.sh

sync-labels:
	./scripts/sync-labels.sh
