.PHONY: install dev up down

install:
    pnpm install

dev:
    pnpm dev

up:
    docker compose -f infra/docker-compose/docker-compose.yml up -d --build

down:
    docker compose -f infra/docker-compose/docker-compose.yml down
