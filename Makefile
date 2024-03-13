# run-venv:
# 	source venv/bin/activate

run-client:
	@cd ./paramount/client/ && pnpm dev

run-server:
	@gunicorn --bind :9001 --workers 1 --threads 8 --timeout 0 paramount.server.wsgi:app

run: run-server run-client

build-client:
	@cd ./paramount/client && pnpm build

docker-build-client:
	@docker build -t paramount-client -f Dockerfile.client .

docker-run-client:
	@docker run -dp 3002:3002 paramount-client

docker-build-server:
	@docker build -t paramount-server -f Dockerfile.server .

docker-run-server:
	@docker run -dp 9001:9001 paramount-server