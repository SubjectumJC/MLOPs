docker-up:      ## Build & levanta en segundo plano
	docker compose up -d --build

docker-down:    ## Apaga y borra contenedores
	docker compose down

logs-api:
	docker compose logs -f api

logs-ui:
	docker compose logs -f ui

train:          ## Ejecuta entrenamiento manual
	docker compose run --rm training
