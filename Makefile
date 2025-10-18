.PHONY: crawl parse etl index up

crawl:
	python -m scraper.crawl

parse:
	python -m scraper.parse

etl:
	python -m pipeline.run

index:
	python -m pipeline.run

up:
	docker-compose up --build
