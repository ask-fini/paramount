# run-venv:
# 	source venv/bin/activate

run-client:
	@cd client & pnpm dev

run-server:
	@gunicorn --bind :9001 --workers 1 --threads 8 --timeout 0 paramount.server.wsgi:app

run-ui:
	@paramount --server.port 9000

run:
	make run-server & make run-client