up:
	docker compose up --build -d

down:
	docker compose down --remove-orphans

sample-video:
	docker compose run --rm api python scripts/generate_sample.py

