ROOT_DIR := $(or ${ROOT_DIR},$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST)))))
TAG ?= $(shell echo $(shell git describe --tags --exact-match 2>/dev/null || ( [ -n "${BRANCH_NAME}" ] && echo "${BRANCH_NAME}" || git rev-parse --abbrev-ref HEAD )) | tr '/' '-')
DOCKER_DEFAULT_PLATFORM=linux/amd64

.EXPORT_ALL_VARIABLES:

init:
	poetry install --verbose
	poetry run playwright install chromium

docker_login:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 345162713151.dkr.ecr.us-east-1.amazonaws.com

build:
	docker compose build

run_docker: build
	docker compose run --service-ports --rm collector

run:
	poetry run uvicorn app:app --reload --log-config=log_conf.yaml

.PHONY: push
push: docker_login build
	docker tag revrod/linkedin-collector:${TAG} 345162713151.dkr.ecr.us-east-1.amazonaws.com/revrod/linkedin-collector:${TAG}
	docker push 345162713151.dkr.ecr.us-east-1.amazonaws.com/revrod/linkedin-collector:${TAG}

deploy:
	poetry run python deployer.py deploy

.PHONY: format
format:
	poetry run ruff format .
	poetry run ruff check --fix-only .

.PHONY: lint
lint: # format
	poetry check
	poetry lock --check
	poetry run ruff check .
	git diff ${GIT_DIFF_FLAGS} --exit-code

.PHONY: test
test:
	poetry run pytest --verbose -s -m $(or ${TEST_MARKER},'') -k $(or ${TEST_FUNC},'') --cov=$(or ${TEST},'.') $(or ${TEST},'.')
